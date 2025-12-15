import json
import time

from uuid import uuid4
from aiohttp.web_response import StreamResponse
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from loguru import logger
from base_rag.database.cache_redis import QA
from base_rag.database.index_milvus import VecIndex
from base_rag.database.match_keyword_es import ESNote
from base_rag.faq.index_faq import FAQVecIndex
from base_rag.rag_layer.embedding import get_embedding
from base_rag.rag_layer.ranker import rank
from llm_stream import async_chat
from llm import chat
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"])


class QueryRequest(BaseModel):
    query: str
    history: list = []

# 异步的回答
async def stream_answer(answer, session_id, query_type, start_time):
    for char in answer:
        yield {"token": char, "session_id": session_id, "query_type": query_type}
    yield {"token": "", "complete": True, "processing_time": time.time() - start_time}

# 异步LLM
async def stream_llm(prompt, query, history, session_id, query_type, start_time):
    chunks = []
    system_prompt = "你是一个热点文案撰写专家，根据提供的信息分析出热点营销的模板，之后请根据用户问题的要求，生成相应热点营销文案。要求：新颖，以引流为主。"
    stream = async_chat(prompt, history, system_prompt)
    async for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            token = chunk.choices[0].delta.content
            chunks.append(token)
            yield {"token": token, "session_id": session_id, "query_type": query_type}
        QA(query=query,answer = "".join(chunks)).save()
        yield {"token": "", "complete": True, "processing_time": time.time() - start_time}


# 异步相应
async def stream_response(query, history, session_id):
    stat_time = time.time()
    # 1.cache 命中
    cached = QA.find(QA.query == query).all()
    if cached:
        async for chunk in stream_answer(cached[0].answer, session_id, "cache", stat_time):
            yield chunk
        return

    # 2. FAQ 命中
    faq_answer = FAQVecIndex("faq").search(get_embedding(query),topk=1)
    if faq_answer.score and faq_answer[0].score> 0.82:
        for chunk in stream_answer(faq_answer[0].answer, session_id, "faq", stat_time):
            yield chunk
        return

    # 3. 是否要查RAG数据库
    _prompt = f"请判断用户问题是否需要搜索知识库，知识库中包含的数据有关于美妆，面霜、粉底液、护手霜等热点模板，如果用户问题需要这些热点模板，请返回true，否则返回false。不要回复其他内容。这是是用户的问题：{query}"
    need_rag = chat(_prompt, history)
    logger.info(f"是否需要知识库need_rag:{need_rag}")
    if need_rag.lower() == "true":
        docs_vec = VecIndex("note").search(get_embedding(query))
        docs_es = ESNote.query(query)
        docs = set(docs_vec+docs_es)
        for doc in docs:
            doc.score = rank(doc.parent, query)
        filtered = [doc for doc in docs if doc.score > 0.7]
        ranked = sorted(filtered, key=lambda x: x.score, reverse=True)
        logger.info(f"搜索结果:{ranked}")

        if ranked:
            reference = "\n".join(f"{doc.parent}"for doc in ranked)
            prompt = f"请根据以下参考内容回答问题：\n{reference}\n问题：{query}\n答案："
            async for chunk in stream_llm(prompt, query, history, session_id, "rag_llm", stat_time):
                yield chunk
            else:
                async for chunk in stream_llm(query, query, history, session_id, "llm", stat_time):
                    yield chunk

    else:
        async for chunk in stream_llm(query, query, history, session_id, "llm", stat_time):
            yield chunk



@app.post("/api/query/stream")
async def query_stream(request: QueryRequest):
    sid = str(uuid4())
    return StreamResponse((f"data: {json.dumps(chunk)}\n\n" async for chunk in stream_response(request.query, request.history, sid)),
                            media_type="text/event-stream",headers ={"Cache-Control": "no-cache","Connection":"keep-alive"})


@app.websocket("api/websocket")
async def websocket_endpoint(websocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        query = data.get("query").strip()
        history = data.get("history", [])
        if not query:
            await websocket.send_json({"type":"error","error": "请输入查询内容"})
            continue
        sid = str(uuid4())
        await websocket.send_json({"type":"start","session_id":sid})
        async for chunk in stream_response(query, history, sid):
            if chunk.get("complete"):
                await websocket.send_json({"type":"end","complete":True,"session_id":sid,"processing_time":chunk.get("processing_time",0)})
            else:
                await websocket.send_json({"type": "token", "token": chunk.get("token", ""), "session_id": chunk.get("session_id", ""), "query_type": chunk.get("query_type", "unknown")})

