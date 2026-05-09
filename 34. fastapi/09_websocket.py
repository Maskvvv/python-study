"""
09. WebSocket 实时通信 🔌
=====================================

亲爱的主人，WebSocket 可以让服务器主动给客户端推送消息哦！
聊天室、实时通知、股票行情...都离不开它～
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List
import json
import asyncio

app = FastAPI(title="WebSocket 实时通信")


# ============================================================
# 一、最简单的 WebSocket
# ============================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"收到消息：{data}")
    except WebSocketDisconnect:
        print("客户端断开连接")


# 测试方式：
# 1. 浏览器控制台：
#    const ws = new WebSocket("ws://127.0.0.1:8000/ws")
#    ws.onmessage = (e) => console.log(e.data)
#    ws.send("Hello!")
#
# 2. 或者访问下面的 HTML 页面


# ============================================================
# 二、聊天室 HTML 页面
# ============================================================

html = """
<!DOCTYPE html>
<html>
<head>
    <title>FastAPI 聊天室 💬</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; }
        #chatbox { border: 1px solid #ccc; height: 300px; overflow-y: scroll; padding: 10px; }
        .msg { margin: 5px 0; padding: 5px 10px; border-radius: 10px; }
        .me { background: #007bff; color: white; text-align: right; }
        .other { background: #e9ecef; text-align: left; }
        .system { color: #6c757d; text-align: center; font-style: italic; }
        #input { display: flex; gap: 10px; margin-top: 10px; }
        #message { flex: 1; padding: 8px; }
        button { padding: 8px 16px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>🎀 FastAPI 聊天室</h1>
    <div id="chatbox"></div>
    <div id="input">
        <input id="message" type="text" placeholder="输入消息..." />
        <button onclick="send()">发送</button>
    </div>
    <script>
        const ws = new WebSocket("ws://127.0.0.1:8000/chat");
        const chatbox = document.getElementById("chatbox");
        const input = document.getElementById("message");

        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            const div = document.createElement("div");
            div.className = data.type === "system" ? "msg system" :
                           data.sender === "我" ? "msg me" : "msg other";
            div.textContent = data.sender + ": " + data.message;
            chatbox.appendChild(div);
            chatbox.scrollTop = chatbox.scrollHeight;
        };

        function send() {
            const msg = input.value;
            if (msg) {
                ws.send(msg);
                input.value = "";
            }
        }

        input.addEventListener("keypress", function(e) {
            if (e.key === "Enter") send();
        });
    </script>
</body>
</html>
"""


@app.get("/chat-page")
async def chat_page():
    return HTMLResponse(html)


# ============================================================
# 三、聊天室 - 连接管理器
# ============================================================

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

    async def send_personal(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)


manager = ConnectionManager()


@app.websocket("/chat")
async def websocket_chat(websocket: WebSocket):
    await manager.connect(websocket)
    await manager.broadcast({"sender": "系统", "message": "有人加入了聊天室！", "type": "system"})

    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast({"sender": "访客", "message": data, "type": "chat"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast({"sender": "系统", "message": "有人离开了聊天室", "type": "system"})


# ============================================================
# 四、WebSocket + 认证
# ============================================================

@app.websocket("/ws-secure")
async def websocket_secure(websocket: WebSocket, token: str = ""):
    if token != "my-secret-token":
        await websocket.close(code=4001, reason="认证失败")
        return

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"安全消息：{data}")
    except WebSocketDisconnect:
        pass


# 连接方式：new WebSocket("ws://127.0.0.1:8000/ws-secure?token=my-secret-token")


# ============================================================
# 五、服务器推送（定时发送）
# ============================================================

@app.websocket("/ws-push")
async def websocket_push(websocket: WebSocket):
    await websocket.accept()
    counter = 0
    try:
        while True:
            counter += 1
            await websocket.send_json({
                "counter": counter,
                "message": f"这是第 {counter} 次推送",
                "timestamp": str(asyncio.get_event_loop().time()),
            })
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        print("推送客户端断开")


# ============================================================
# 六、WebSocket 与 HTTP 共存
# ============================================================

@app.get("/ws-info")
async def websocket_info():
    return {
        "message": "WebSocket 端点列表",
        "endpoints": {
            "/ws": "简单回显",
            "/chat": "聊天室",
            "/ws-secure": "需要认证的 WebSocket",
            "/ws-push": "服务器定时推送",
        },
        "chat_page": "/chat-page",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("09_websocket:app", host="127.0.0.1", port=8000, reload=True)
