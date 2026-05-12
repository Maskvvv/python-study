"""
13. AI API 集成 🤖
=====================================

亲爱的主人，这节我们学习如何把 FastAPI 和 AI 大模型结合起来！
这是当下最热门的技术组合～
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, AsyncIterator
import asyncio
import json
import time
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="AI API 集成")

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


# ============================================================
# 一、OpenAI API 集成
# ============================================================
# pip install openai

from openai import OpenAI, AsyncOpenAI

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("BASE_URL")

client = OpenAI(base_url=base_url, api_key=api_key)

async_client = AsyncOpenAI(base_url=base_url, api_key=api_key)


# ============================================================
# 二、基础对话（非流式）
# ============================================================

class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="用户输入")
    model: str = Field("kimi-k2.6", description="模型名称")
    max_tokens: int = Field(1024, ge=1, le=4096)
    temperature: float = Field(1, ge=0, le=2)


class ChatResponse(BaseModel):
    content: str
    model: str
    usage: dict


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = await async_client.chat.completions.create(
            model=request.model,
            messages=[{"role": "user", "content": request.prompt}],
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )
        return ChatResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 三、流式对话（SSE）—— 最核心！
# ============================================================

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    async def event_stream():
        try:
            stream = await async_client.chat.completions.create(
                model=request.model,
                messages=[{"role": "user", "content": request.prompt}],
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"

            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream", headers=SSE_HEADERS)


# ============================================================
# 四、多轮对话（带上下文）
# ============================================================

class Message(BaseModel):
    role: str = Field(..., pattern="^(system|user|assistant)$")
    content: str


class MultiTurnRequest(BaseModel):
    messages: list[Message] = Field(..., min_length=1)
    model: str = "kimi-k2.6"
    max_tokens: int = 1024
    temperature: float = 1


@app.post("/chat/multi-turn")
async def chat_multi_turn(request: MultiTurnRequest):
    try:
        response = await async_client.chat.completions.create(
            model=request.model,
            messages=[msg.model_dump() for msg in request.messages],
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )
        return {"content": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/multi-turn/stream")
async def chat_multi_turn_stream(request: MultiTurnRequest):
    async def event_stream():
        try:
            stream = await async_client.chat.completions.create(
                model=request.model,
                messages=[msg.model_dump() for msg in request.messages],
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                stream=True,
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield f"data: {json.dumps({'token': chunk.choices[0].delta.content}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream", headers=SSE_HEADERS)


# ============================================================
# 五、System Prompt 模式
# ============================================================

class SystemChatRequest(BaseModel):
    prompt: str
    system_prompt: str = "你是一个有帮助的AI助手。"
    model: str = "kimi-k2.6"


@app.post("/chat/with-system")
async def chat_with_system(request: SystemChatRequest):
    try:
        response = await async_client.chat.completions.create(
            model=request.model,
            messages=[
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.prompt},
            ],
        )
        return {"content": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 六、流式对话前端页面
# ============================================================

chat_html = """
<!DOCTYPE html>
<html>
<head>
    <title>AI 对话 🤖</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 700px; margin: 30px auto; padding: 0 20px; }
        #chat { border: 1px solid #ddd; border-radius: 8px; height: 400px; overflow-y: auto; padding: 15px; background: #f8f9fa; }
        .msg { margin: 8px 0; padding: 10px 14px; border-radius: 12px; max-width: 80%; white-space: pre-wrap; }
        .user { background: #007bff; color: white; margin-left: auto; text-align: right; }
        .assistant { background: white; border: 1px solid #ddd; }
        .system { background: #fff3cd; color: #856404; text-align: center; font-size: 12px; }
        #input-area { display: flex; gap: 10px; margin-top: 15px; }
        #prompt { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 6px; resize: none; }
        button { padding: 10px 20px; cursor: pointer; border: none; border-radius: 6px; background: #007bff; color: white; }
        button:hover { background: #0056b3; }
        button:disabled { background: #6c757d; cursor: not-allowed; }
        .typing::after { content: '▊'; animation: blink 0.5s infinite; }
        @keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0; } }
    </style>
</head>
<body>
    <h1>🤖 AI 流式对话</h1>
    <div id="chat"></div>
    <div id="input-area">
        <textarea id="prompt" rows="2" placeholder="输入消息..."></textarea>
        <button id="send-btn" onclick="send()">发送</button>
    </div>

    <script>
        const chat = document.getElementById("chat");
        const promptInput = document.getElementById("prompt");
        const sendBtn = document.getElementById("send-btn");
        let messages = [];

        function addMessage(role, content) {
            const div = document.createElement("div");
            div.className = `msg ${role}`;
            div.textContent = content;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
            return div;
        }

        async function send() {
            const text = promptInput.value.trim();
            if (!text) return;

            addMessage("user", text);
            messages.push({ role: "user", content: text });
            promptInput.value = "";
            sendBtn.disabled = true;

            const assistantDiv = addMessage("assistant", "");
            assistantDiv.classList.add("typing");

            try {
                const response = await fetch("/chat/multi-turn/stream", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ messages: messages }),
                });

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let fullContent = "";

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    const text = decoder.decode(value);
                    for (const line of text.split("\\n")) {
                        if (line.startsWith("data: ")) {
                            const data = JSON.parse(line.slice(6));
                            if (data.done) break;
                            if (data.token) {
                                fullContent += data.token;
                                assistantDiv.textContent = fullContent;
                                chat.scrollTop = chat.scrollHeight;
                            }
                        }
                    }
                }

                messages.push({ role: "assistant", content: fullContent });
            } catch (e) {
                assistantDiv.textContent = "错误：" + e.message;
            }

            assistantDiv.classList.remove("typing");
            sendBtn.disabled = false;
        }

        promptInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
        });
    </script>
</body>
</html>
"""


@app.get("/chat-page")
async def chat_page():
    return HTMLResponse(chat_html)


# ============================================================
# 七、模拟 AI 流式输出（无需 API Key 也能测试）
# ============================================================
# 如果你没有 OpenAI API Key，可以用这个模拟端点来测试

class MockChatRequest(BaseModel):
    prompt: str
    model: str = "mock-gpt"


MOCK_RESPONSES = {
    "default": "你好！我是模拟的 AI 助手。这个端点不需要 API Key，可以用来测试 SSE 流式输出的效果。在实际项目中，你需要把这里替换成真实的 OpenAI API 调用。",
    "fastapi": "FastAPI 是一个现代、快速的 Web 框架，用于构建 API。它的主要特点包括：\n\n1. **快速**：性能媲美 NodeJS 和 Go\n2. **自动文档**：内置 Swagger UI 和 ReDoc\n3. **类型验证**：基于 Pydantic 的自动数据验证\n4. **异步支持**：原生支持 async/await\n5. **依赖注入**：优雅的 DI 系统\n\n非常适合用来构建 AI 应用的后端服务！",
    "python": "Python 是一门优雅而强大的编程语言，广泛应用于：\n\n- Web 开发\n- 数据科学\n- 人工智能\n- 自动化脚本\n\n它的语法简洁明了，是学习编程的绝佳选择！",
}


@app.post("/chat/mock-stream")
async def chat_mock_stream(request: MockChatRequest):
    async def event_stream():
        prompt_lower = request.prompt.lower()
        response_text = MOCK_RESPONSES.get(
            next((k for k in MOCK_RESPONSES if k in prompt_lower), "default"),
            MOCK_RESPONSES["default"],
        )

        for char in response_text:
            yield f"data: {json.dumps({'token': char}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.03)

        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream", headers=SSE_HEADERS)


# ============================================================
# 八、API Key 管理（依赖注入）
# ============================================================

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)

VALID_API_KEYS = {"sk-demo-key-1", "sk-demo-key-2"}


async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials or credentials.credentials not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="无效的 API Key")
    return credentials.credentials


@app.post("/chat/auth-stream")
async def chat_auth_stream(request: ChatRequest, api_key: str = Depends(verify_api_key)):
    async def event_stream():
        try:
            stream = await async_client.chat.completions.create(
                model=request.model,
                messages=[{"role": "user", "content": request.prompt}],
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                stream=True,
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield f"data: {json.dumps({'token': chunk.choices[0].delta.content}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream", headers=SSE_HEADERS)


# ============================================================
# 九、多模型切换
# ============================================================

AVAILABLE_MODELS = {
    "gpt-4o": "OpenAI GPT-4o（最强）",
    "kimi-k2.6": "OpenAI GPT-4o Mini（性价比高）",
    "gpt-3.5-turbo": "OpenAI GPT-3.5 Turbo（经典）",
    "mock-gpt": "模拟模型（无需 API Key）",
}


@app.get("/models")
async def list_models():
    return {"models": AVAILABLE_MODELS}


# ============================================================
# 十、生产环境建议
# ============================================================
"""
1. API Key 安全
   - 不要硬编码 API Key，使用环境变量
   - export OPENAI_API_KEY="sk-xxx"
   - 或者用 .env 文件 + python-dotenv

2. 速率限制
   - 使用 slowapi 等库限制每用户请求频率
   - 防止 API 被滥用导致费用暴涨

3. 错误处理
   - 捕获 openai.RateLimitError（429）
   - 捕获 openai.APIConnectionError（网络问题）
   - 捕获 openai.APIStatusError（其他错误）
   - 实现自动重试机制

4. 流式响应注意事项
   - 设置 X-Accel-Buffering: no（Nginx 环境必须）
   - 设置 Cache-Control: no-cache
   - 注意超时设置（大模型响应可能较慢）

5. 异步客户端
   - 始终使用 AsyncOpenAI，不要用同步客户端
   - 同步客户端会阻塞事件循环，影响并发性能

6. 连接池
   - 复用 AsyncOpenAI 实例，不要每次请求都创建
   - 可以用依赖注入来管理客户端生命周期
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("13_ai_integration:app", host="127.0.0.1", port=8000, reload=True)
