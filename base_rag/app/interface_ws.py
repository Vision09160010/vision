import chainlit as cl
import json
import websockets
WEBSOCKET_URL = "ws://localhost:8099/api/ws"
@cl.on_chat_start
async def start():
    await cl.Message(content="你好，今天要写点什么文案呢").send()
    cl.user_session.set("history", [])

@cl.on_message
async def handle_msg(message: cl.Message):
    msg = cl.Message("")
    await msg.send()
    history = cl.user_session.get("history",[])
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        await websocket.send(json.dumps({"query":message.content,"history":history}))
        answer = ""
        while True:
            response = await websocket.recv()
            response = json.loads(response)
            if response.get("Type") == "token":
                token = data.get("token","")
                if token:
                    answer += token
                    await msg.stream_token(token)
            elif data.get("type") == "end":
                break
        history.append({"role":"user","content":message.content})
        history.append({"role":"assistant","content":answer})
        cl.user_session.set("history",history)

