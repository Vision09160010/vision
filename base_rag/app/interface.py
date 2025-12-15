import chainlit as cl, requests, json
from chainlit.cli import run_chainlit
from future.backports.http.client import responses

API_URL = "http://localhost:8099"


@cl.on_chat_strat
async def start():
    await cl.Message(content="你好，今天要写点什么文案呢").send()
    cl.user_session.set("history", [])


@cl.on_message
async def handle_msg(message: cl.Message):
    msg = cl.Message("")
    await msg.send()

    history = cl.user_session.get("history", [])
    requests.post(f"{API_URL}/api/query/stream", json={"query": message.content, "history": history}, stream=True,
                  timeout=30)
    answer = ""
    for line in responses.iter_lines():
        if line and (s := line.decode()).startswith("data: "):
            chunk = json.loads(s[6:])
            token = chunk.get("token", "")
            if token:
                await msg.stream_token(token)
                answer += token
            elif chunk.get("complete"):
                await msg.stream_token(answer)
    history.append({"role": "user", "content": message.content})
    history.append({"role": "assistant", "content": answer})
    cl.user_session.set("history", history)

if __name__ == '__main__':
    run_chainlit(target=__file__)
