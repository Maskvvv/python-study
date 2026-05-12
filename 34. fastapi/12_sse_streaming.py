"""
12. SSE 与流式响应 🌊
=====================================

亲爱的主人，SSE 是 AI 流式输出的核心技术！
ChatGPT 那种"一个字一个字蹦出来"的效果，就是靠 SSE 实现的！
"""

from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional
import asyncio
import json
import time

app = FastAPI(title="SSE 与流式响应")


# ============================================================
# 一、StreamingResponse 基础
# ============================================================
# FastAPI 的 StreamingResponse 可以把生成器的内容逐步发送给客户端
# 不用等所有数据准备好再返回！

@app.get("/stream-basic")
async def stream_basic():
    async def generate():
        for i in range(10):
            yield f"第 {i + 1} 条数据\n\n"
            await asyncio.sleep(0.5)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ⚠️ 为什么不用 text/plain？
#   浏览器会对 text/plain 做缓冲，等所有数据到齐才显示！
#   改用 text/event-stream（SSE 格式），浏览器会逐条处理。
#
# 关键 Headers 说明：
#   Cache-Control: no-cache     → 禁止缓存，数据即时传递
#   X-Accel-Buffering: no       → 禁止 Nginx 代理缓冲（生产环境必备）
#   Connection: keep-alive      → 保持连接不断开
#
# 测试方式：
#   1. 浏览器直接访问 → 会看到数据逐条出现
#   2. curl http://127.0.0.1:8000/stream-basic → 终端也能看到流式效果
#   3. 用 JS 的 EventSource 接收 → 最标准的方式


# ============================================================
# 二、SSE（Server-Sent Events）协议
# ============================================================
"""
SSE 是一种基于 HTTP 的服务器推送协议，格式如下：

  data: 消息内容\n
  \n

每条消息以 "data: " 开头，以两个换行符结束。
浏览器有原生的 EventSource API 来接收 SSE。

SSE vs WebSocket：
┌──────────────┬──────────────────┬──────────────────┐
│     特性      │      SSE         │    WebSocket     │
├──────────────┼──────────────────┼──────────────────┤
│ 方向          │ 服务器→客户端     │ 双向             │
│ 协议          │ HTTP             │ WS               │
│ 重连          │ 自动重连         │ 需手动           │
│ 数据格式      │ 文本             │ 文本/二进制      │
│ 浏览器API     │ EventSource     │ WebSocket        │
│ 适合场景      │ AI流式输出、通知  │ 聊天、游戏       │
└──────────────┴──────────────────┴──────────────────┘

AI 场景首选 SSE，因为：
  - 大模型输出是单向的（服务器→客户端）
  - SSE 基于 HTTP，兼容性更好
  - 自动重连，断线不怕
"""

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


@app.get("/sse-basic")
async def sse_basic():
    async def event_stream():
        for i in range(5):
            data = json.dumps({"count": i + 1, "message": f"这是第 {i + 1} 条推送"}, ensure_ascii=False)
            yield f"data: {data}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(event_stream(), media_type="text/event-stream", headers=SSE_HEADERS)


# ============================================================
# 三、SSE 带事件类型
# ============================================================
# SSE 支持给消息分类，客户端可以只监听特定类型的事件

@app.get("/sse-events")
async def sse_events():
    async def event_stream():
        for i in range(6):
            event_type = "progress" if i < 5 else "complete"
            data = json.dumps({
                "step": i + 1,
                "progress": min((i + 1) * 20, 100),
                "message": "处理中..." if i < 5 else "完成！",
            }, ensure_ascii=False)
            yield f"event: {event_type}\ndata: {data}\n\n"
            await asyncio.sleep(0.8)

    return StreamingResponse(event_stream(), media_type="text/event-stream", headers=SSE_HEADERS)


# 客户端监听方式：
# const es = new EventSource("/sse-events")
# es.addEventListener("progress", (e) => console.log(JSON.parse(e.data)))
# es.addEventListener("complete", (e) => { console.log("Done!"); es.close() })


# ============================================================
# 四、SSE 带 ID 和重连
# ============================================================

@app.get("/sse-with-id")
async def sse_with_id(last_event_id: Optional[int] = None):
    start = last_event_id + 1 if last_event_id else 0

    async def event_stream():
        for i in range(start, start + 5):
            data = json.dumps({"message": f"消息 #{i}"}, ensure_ascii=False)
            yield f"id: {i}\ndata: {data}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(event_stream(), media_type="text/event-stream", headers=SSE_HEADERS)


# 客户端断线重连时，浏览器会自动带上 Last-Event-ID 请求头
# 服务器据此从断点续传


# ============================================================
# 五、模拟 AI 流式输出（核心！）
# ============================================================

async def mock_ai_stream(prompt: str):
    """模拟大模型的流式输出效果"""
    response = f"收到你的问题：「{prompt}」，让我来回答：\n\n" \
               f"这是一个模拟的 AI 流式响应。在实际项目中，" \
               f"这里会调用 OpenAI / Claude 等大模型的流式 API。" \
               f"每个 token 会逐步返回，就像 ChatGPT 那样一个字一个字地蹦出来！" \
               f"\n\n希望这个演示能帮助你理解 SSE 的工作原理 🎀"

    for char in response:
        yield char
        await asyncio.sleep(0.05)


@app.get("/ai-stream")
async def ai_stream(prompt: str = "你好"):
    async def event_stream():
        async for char in mock_ai_stream(prompt):
            data = json.dumps({"token": char}, ensure_ascii=False)
            yield f"data: {data}\n\n"

        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream", headers=SSE_HEADERS)


# ============================================================
# 六、SSE 前端页面（交互式演示）
# ============================================================

sse_html = """
<!DOCTYPE html>
<html>
<head>
    <title>SSE 流式演示 🌊</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 700px; margin: 30px auto; padding: 0 20px; }
        h1 { color: #333; }
        .box { border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 15px 0; }
        #output { white-space: pre-wrap; min-height: 100px; background: #f8f9fa; padding: 12px; border-radius: 6px; font-size: 14px; }
        .btn { padding: 8px 16px; margin: 5px; cursor: pointer; border: none; border-radius: 4px; background: #007bff; color: white; }
        .btn:hover { background: #0056b3; }
        .btn-stop { background: #dc3545; }
        .btn-stop:hover { background: #c82333; }
        #progress-bar { width: 100%; height: 20px; background: #e9ecef; border-radius: 10px; overflow: hidden; }
        #progress-fill { height: 100%; background: #007bff; width: 0%; transition: width 0.3s; }
        .status { color: #6c757d; font-size: 12px; margin-top: 5px; }
    </style>
</head>
<body>
    <h1>🌊 SSE 流式响应演示</h1>

    <div class="box">
        <h3>1. 基础 SSE</h3>
        <button class="btn" onclick="startBasic()">开始推送</button>
        <button class="btn btn-stop" onclick="stopAll()">停止</button>
        <div id="basic-output" class="status">点击按钮开始...</div>
    </div>

    <div class="box">
        <h3>2. 进度推送</h3>
        <button class="btn" onclick="startProgress()">开始任务</button>
        <div id="progress-bar"><div id="progress-fill"></div></div>
        <div id="progress-status" class="status">等待开始...</div>
    </div>

    <div class="box">
        <h3>3. AI 流式输出</h3>
        <input id="prompt" type="text" value="什么是FastAPI？" style="width:70%; padding:8px;" />
        <button class="btn" onclick="startAI()">发送</button>
        <div id="ai-output"></div>
        <div id="ai-status" class="status">输入问题后点击发送...</div>
    </div>

    <script>
        let currentES = null;

        function stopAll() {
            if (currentES) { currentES.close(); currentES = null; }
        }

        function startBasic() {
            stopAll();
            const output = document.getElementById("basic-output");
            output.textContent = "连接中...";
            currentES = new EventSource("/sse-basic");
            currentES.onmessage = (e) => { output.textContent = JSON.parse(e.data).message; };
            currentES.onerror = () => { output.textContent = "连接关闭"; currentES.close(); };
        }

        function startProgress() {
            stopAll();
            const fill = document.getElementById("progress-fill");
            const status = document.getElementById("progress-status");
            fill.style.width = "0%";
            status.textContent = "处理中...";
            currentES = new EventSource("/sse-events");
            currentES.addEventListener("progress", (e) => {
                const data = JSON.parse(e.data);
                fill.style.width = data.progress + "%";
                status.textContent = data.message + " (" + data.progress + "%)";
            });
            currentES.addEventListener("complete", (e) => {
                const data = JSON.parse(e.data);
                fill.style.width = "100%";
                status.textContent = "✅ " + data.message;
                currentES.close();
            });
        }

        function startAI() {
            stopAll();
            const prompt = document.getElementById("prompt").value;
            const output = document.getElementById("ai-output");
            const status = document.getElementById("ai-status");
            output.textContent = "";
            status.textContent = "AI 思考中...";
            currentES = new EventSource("/ai-stream?prompt=" + encodeURIComponent(prompt));
            currentES.onmessage = (e) => {
                const data = JSON.parse(e.data);
                if (data.done) {
                    status.textContent = "✅ 生成完成";
                    currentES.close();
                } else {
                    output.textContent += data.token;
                }
            };
        }
    </script>
</body>
</html>
"""


@app.get("/sse-demo")
async def sse_demo_page():
    return HTMLResponse(sse_html)


# ============================================================
# 七、用 POST 发起 SSE（更实用的模式）
# ============================================================
# 标准 SSE 只支持 GET，但 AI 场景通常需要 POST 发送复杂请求
# 解决方案：用 StreamingResponse + 自定义格式

class ChatRequest(BaseModel):
    prompt: str
    max_tokens: int = 100
    temperature: float = 0.7


@app.post("/ai-chat")
async def ai_chat(request: ChatRequest):
    async def event_stream():
        response_text = (
            f"你问：「{request.prompt}」\n\n"
            f"这是模拟的 AI 回复。temperature={request.temperature}，"
            f"max_tokens={request.max_tokens}。\n\n"
            f"在实际项目中，这里会调用 OpenAI 的 chat.completions.create() "
            f"并设置 stream=True，然后逐个返回 token。"
        )

        for char in response_text:
            data = json.dumps({"token": char}, ensure_ascii=False)
            yield f"data: {data}\n\n"
            await asyncio.sleep(0.03)

        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream", headers=SSE_HEADERS)


# ============================================================
# 八、JSON 流式响应（非 SSE 格式）
# ============================================================
# 有些前端框架更喜欢每行一个 JSON（NDJSON 格式）

@app.get("/json-stream")
async def json_stream():
    async def generate():
        for i in range(5):
            yield json.dumps({"index": i, "value": f"数据{i}", "timestamp": time.time()}, ensure_ascii=False) + "\n"
            await asyncio.sleep(0.5)

    return StreamingResponse(generate(), media_type="application/x-ndjson")


# ============================================================
# 九、SSE 工具函数（推荐封装）
# ============================================================

class SSEMessage:
    """SSE 消息构建器"""

    @staticmethod
    def data(data: dict) -> str:
        payload = json.dumps(data, ensure_ascii=False)
        return f"data: {payload}\n\n"

    @staticmethod
    def event(event: str, data: dict) -> str:
        payload = json.dumps(data, ensure_ascii=False)
        return f"event: {event}\ndata: {payload}\n\n"

    @staticmethod
    def id(event_id: int, data: dict) -> str:
        payload = json.dumps(data, ensure_ascii=False)
        return f"id: {event_id}\ndata: {payload}\n\n"

    @staticmethod
    def comment(text: str) -> str:
        return f": {text}\n\n"

    @staticmethod
    def retry(seconds: int) -> str:
        return f"retry: {seconds * 1000}\n\n"


@app.get("/sse-tool-demo")
async def sse_tool_demo():
    async def event_stream():
        yield SSEMessage.retry(5)
        yield SSEMessage.comment("这是注释，客户端会忽略")
        yield SSEMessage.data({"message": "普通消息"})
        yield SSEMessage.event("update", {"progress": 50})
        yield SSEMessage.id(1, {"message": "带ID的消息"})
        yield SSEMessage.event("done", {"message": "完成！"})

    return StreamingResponse(event_stream(), media_type="text/event-stream", headers=SSE_HEADERS)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("12_sse_streaming:app", host="127.0.0.1", port=8000, reload=True)
