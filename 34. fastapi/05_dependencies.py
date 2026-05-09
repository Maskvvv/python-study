"""
05. 依赖注入系统 💉
=====================================

亲爱的主人，依赖注入是 FastAPI 最强大的特性之一！
它让你的代码更优雅、更可测试、更可复用～
"""

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="依赖注入系统")


# ============================================================
# 一、什么是依赖注入？
# ============================================================
"""
依赖注入（Dependency Injection）是一种设计模式：
  - 你的代码需要某些"依赖"才能工作
  - 不是自己创建依赖，而是由外部"注入"
  - FastAPI 会在请求时自动帮你调用依赖函数

好处：
  1. 代码复用 - 同一个依赖可以给多个路由使用
  2. 共享逻辑 - 比如数据库连接、认证检查
  3. 易于测试 - 可以轻松替换依赖
"""


# ============================================================
# 二、最简单的依赖
# ============================================================

def common_parameters(q: Optional[str] = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}


@app.get("/items")
async def read_items(commons: dict = Depends(common_parameters)):
    return {"message": "获取物品列表", "params": commons}


@app.get("/users")
async def read_users(commons: dict = Depends(common_parameters)):
    return {"message": "获取用户列表", "params": commons}


# Depends(common_parameters) 告诉 FastAPI：
#   "请调用 common_parameters()，把结果传给我"
# 多个路由共享同一个依赖，不用重复写参数！


# ============================================================
# 三、类作为依赖
# ============================================================

class CommonQueryParams:
    def __init__(self, q: Optional[str] = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit


@app.get("/items-class")
async def read_items_class(commons: CommonQueryParams = Depends(CommonQueryParams)):
    return {
        "message": "使用类作为依赖",
        "q": commons.q,
        "skip": commons.skip,
        "limit": commons.limit,
    }


# 简写：commons = Depends() 等同于 commons = Depends(CommonQueryParams)
@app.get("/items-class-short")
async def read_items_class_short(commons: CommonQueryParams = Depends()):
    return {"message": "简写形式", "params": commons}


# ============================================================
# 四、子依赖（依赖的依赖）
# ============================================================

def query_extractor(q: Optional[str] = None):
    return q


def query_or_cookie_extractor(
    q: str = Depends(query_extractor),
    last_query: Optional[str] = None,
):
    if not q:
        return last_query
    return q


@app.get("/sub-dependency")
async def read_sub_dependency(query_or_default: str = Depends(query_or_cookie_extractor)):
    return {"query_or_cookie": query_or_default}


# FastAPI 会自动解析依赖链：
# query_or_cookie_extractor → 依赖 query_extractor
# FastAPI 先调用 query_extractor，再把结果传给 query_or_cookie_extractor


# ============================================================
# 五、依赖中的数据库会话模式（模拟）
# ============================================================

class DatabaseSession:
    def __init__(self):
        self.connected = True
        print("  📡 数据库连接已建立")

    def query(self, table: str):
        print(f"  🔍 查询表：{table}")
        return [{"id": 1, "name": "模拟数据"}]

    def close(self):
        self.connected = False
        print("  📡 数据库连接已关闭")


def get_db():
    db = DatabaseSession()
    try:
        yield db
    finally:
        db.close()


@app.get("/db-items")
async def read_db_items(db: DatabaseSession = Depends(get_db)):
    items = db.query("items")
    return {"items": items}


# yield 依赖模式：
#   yield 之前 → 请求前执行（建立连接）
#   yield 的值 → 注入到路由函数
#   yield 之后 → 请求后执行（关闭连接）


# ============================================================
# 六、全局依赖
# ============================================================

def verify_api_key(api_key: str = "default-key"):
    if api_key != "my-secret-key":
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key


# 可以给整个应用添加依赖（这里注释掉，不然所有请求都需要验证）
# app = FastAPI(dependencies=[Depends(verify_api_key)])

# 也可以给某个路由组添加依赖
from fastapi import APIRouter

secure_router = APIRouter(dependencies=[Depends(verify_api_key)])


@secure_router.get("/secure-data")
async def get_secure_data():
    return {"data": "这是需要验证才能看到的数据"}


app.include_router(secure_router)


# ============================================================
# 七、依赖覆盖（测试时超有用！）
# ============================================================

def get_query_param(q: Optional[str] = None):
    return q


@app.get("/override-demo")
async def override_demo(query: Optional[str] = Depends(get_query_param)):
    return {"query": query}


# 测试时可以这样覆盖：
# app.dependency_overrides[get_query_param] = lambda: "fake_query"
# 这样所有依赖 get_query_param 的地方都会收到 "fake_query"


# ============================================================
# 八、实用的依赖示例：分页
# ============================================================

class PaginationParams:
    def __init__(
        self,
        page: int = 1,
        page_size: int = 10,
        max_page_size: int = 100,
    ):
        self.page = max(1, page)
        self.page_size = min(max(1, page_size), max_page_size)
        self.skip = (self.page - 1) * self.page_size
        self.limit = self.page_size


fake_data = [{"id": i, "name": f"Item {i}"} for i in range(1, 51)]


@app.get("/paginated-items")
async def get_paginated_items(pagination: PaginationParams = Depends()):
    items = fake_data[pagination.skip: pagination.skip + pagination.limit]
    return {
        "items": items,
        "page": pagination.page,
        "page_size": pagination.page_size,
        "total": len(fake_data),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("05_dependencies:app", host="127.0.0.1", port=8000, reload=True)
