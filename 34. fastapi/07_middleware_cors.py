"""
07. 中间件与CORS 🛡️
=====================================

亲爱的主人，中间件就像一个"守门员"，每个请求和响应都要经过它！
CORS 则是解决跨域问题的利器～
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time

app = FastAPI(title="中间件与CORS")


# ============================================================
# 一、什么是中间件？
# ============================================================
"""
中间件是一个函数，在每个请求到达路由之前和响应返回之后执行：

  请求 → 中间件（前） → 路由处理 → 中间件（后） → 响应

常见用途：
  - 日志记录
  - 性能监控
  - 认证检查
  - 修改请求/响应
  - CORS 处理
  - Gzip 压缩
"""


# ============================================================
# 二、自定义中间件
# ============================================================

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    # 请求前：记录开始时间
    start_time = time.time()

    # 调用下一个中间件或路由
    response = await call_next(request)

    # 响应后：计算处理时间
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    print(f"  ⏱️ {request.method} {request.url.path} - {process_time:.4f}s")

    return response


@app.get("/timing")
async def timing_demo():
    return {"message": "查看响应头中的 X-Process-Time！"}


# ============================================================
# 三、CORS 中间件（超重要！）
# ============================================================
"""
CORS（跨域资源共享）是什么？

当前端（如 http://localhost:3000）请求后端（如 http://localhost:8000）时，
浏览器会阻止这个请求，因为"域"不同（端口不同也算跨域）。

CORS 中间件告诉浏览器："这些域的请求是允许的！"
"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 参数说明：
# allow_origins   → 允许的源列表，["*"] 表示允许所有（生产环境不推荐）
# allow_credentials → 是否允许携带 Cookie
# allow_methods   → 允许的 HTTP 方法，["*"] 表示所有
# allow_headers   → 允许的请求头，["*"] 表示所有


@app.get("/cors-demo")
async def cors_demo():
    return {"message": "前端可以跨域访问这个接口啦！"}


# ============================================================
# 四、GZip 中间件
# ============================================================
# 自动压缩响应，减少传输数据量

app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.get("/gzip-demo")
async def gzip_demo():
    return {"message": "这是一个很长的响应，会被 GZip 压缩！" * 100}


# ============================================================
# 五、请求日志中间件
# ============================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"  📥 收到请求：{request.method} {request.url}")
    print(f"     客户端：{request.client.host if request.client else 'unknown'}")
    print(f"     User-Agent：{request.headers.get('user-agent', 'unknown')}")

    response = await call_next(request)

    print(f"  📤 返回响应：{response.status_code}")
    return response


@app.get("/logged")
async def logged_route():
    return {"message": "这个请求已经被记录了，看控制台输出！"}


# ============================================================
# 六、异常处理中间件
# ============================================================

@app.middleware("http")
async def catch_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        print(f"  ❌ 未捕获的异常：{exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "服务器内部错误，请稍后重试"},
        )


# ============================================================
# 七、中间件执行顺序
# ============================================================
"""
中间件按添加顺序执行，像洋葱一样：

  请求 → 中间件1前 → 中间件2前 → 中间件3前 → 路由
  响应 ← 中间件1后 ← 中间件2后 ← 中间件3后 ← 路由

所以：
  - 最先添加的中间件最先处理请求，最后处理响应
  - 最后添加的中间件最后处理请求，最先处理响应

添加顺序：
  1. add_process_time_header（第一个添加）
  2. CORS
  3. GZip
  4. log_requests
  5. catch_exceptions（最后添加，最先处理请求）
"""


# ============================================================
# 八、纯 ASGI 中间件
# ============================================================
# 也可以写纯 ASGI 中间件，更底层但更灵活

class CustomASGIMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            print(f"  🔧 ASGI中间件：{scope['method']} {scope['path']}")
        await self.app(scope, receive, send)


app.add_middleware(CustomASGIMiddleware)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("07_middleware_cors:app", host="127.0.0.1", port=8000, reload=True)
