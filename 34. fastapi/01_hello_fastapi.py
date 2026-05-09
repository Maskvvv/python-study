"""
01. Hello FastAPI - 第一个应用 🚀
=====================================

亲爱的主人，让我们从最简单的 FastAPI 应用开始吧！
"""

# ------------------------------------------------------------
# 1. 安装 FastAPI
# ------------------------------------------------------------
# pip install fastapi uvicorn
#
# fastapi  - Web 框架本体
# uvicorn  - ASGI 服务器，用来运行 FastAPI 应用

# ------------------------------------------------------------
# 2. 最简单的 FastAPI 应用
# ------------------------------------------------------------

from fastapi import FastAPI

app = FastAPI(title="我的第一个FastAPI应用", version="0.1.0")


@app.get("/")
async def root():
    return {"message": "Hello, Dear Master! 🎀 Welcome to FastAPI!"}


@app.get("/hello")
async def hello():
    return {"greeting": "你好呀～这是 FastAPI 的世界！"}


# ------------------------------------------------------------
# 3. 运行方式
# ------------------------------------------------------------
# 在终端中运行：
#   uvicorn 01_hello_fastapi:app --reload
#
# 参数说明：
#   01_hello_fastapi  - 文件名（不含.py）
#   :app              - 文件中 FastAPI 实例的变量名
#   --reload          - 代码修改后自动重启（开发时用）
#
# 运行后访问：
#   http://127.0.0.1:8000/          → API 响应
#   http://127.0.0.1:8000/docs      → Swagger UI 交互式文档 ✨
#   http://127.0.0.1:8000/redoc     → ReDoc 文档

# ------------------------------------------------------------
# 4. 路由装饰器
# ------------------------------------------------------------
# FastAPI 用装饰器来定义路由，和 Flask 类似但更强大：
#
# @app.get("/")       → GET 请求
# @app.post("/")      → POST 请求
# @app.put("/")       → PUT 请求（全量更新）
# @app.patch("/")     → PATCH 请求（部分更新）
# @app.delete("/")    → DELETE 请求
#
# 返回值会自动被序列化为 JSON！

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id, "message": f"你请求了第 {item_id} 号物品"}


@app.post("/items")
async def create_item():
    return {"message": "创建了一个新物品！"}


# ------------------------------------------------------------
# 5. 应用生命周期事件
# ------------------------------------------------------------
# 有时候我们需要在应用启动/关闭时做一些事情
# 比如连接数据库、关闭数据库连接

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 应用启动啦！可以在这里初始化数据库连接等")
    yield
    print("👋 应用关闭啦！可以在这里清理资源")


app_with_lifespan = FastAPI(lifespan=lifespan)


@app.get("/lifespan-demo")
async def lifespan_demo():
    return {"message": "这个应用有生命周期管理哦～"}


# ------------------------------------------------------------
# 6. 同步 vs 异步
# ------------------------------------------------------------
# FastAPI 同时支持 async def 和 普通 def：
#
# async def  → 用于异步操作（数据库、HTTP请求等）
# def        → 用于同步操作（CPU密集型、阻塞IO等）
#
# FastAPI 会自动处理！不需要额外配置

@app.get("/sync-endpoint")
def sync_endpoint():
    return {"message": "这是同步函数，FastAPI 也能处理！"}


@app.get("/async-endpoint")
async def async_endpoint():
    return {"message": "这是异步函数，性能更好哦～"}


# ------------------------------------------------------------
# 7. 直接运行
# ------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("01_hello_fastapi:app", host="127.0.0.1", port=8000, reload=True)
