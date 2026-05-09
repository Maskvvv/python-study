"""
04. 响应模型与序列化 📋
=====================================

亲爱的主人，这节我们来学习如何控制 API 的响应格式！
FastAPI 的 response_model 是一个超级实用的功能哦～
"""

from fastapi import FastAPI, Response, status
from fastapi.responses import JSONResponse, PlainTextResponse, HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

app = FastAPI(title="响应模型与序列化")


# ============================================================
# 一、response_model 基础
# ============================================================
# response_model 告诉 FastAPI 返回数据的结构
# 它会自动：
#   1. 过滤掉模型中没有的字段（数据脱敏）
#   2. 验证返回数据的类型
#   3. 在 API 文档中显示响应结构

class UserIn(BaseModel):
    username: str
    password: str
    email: str


class UserOut(BaseModel):
    username: str
    email: str


@app.post("/users", response_model=UserOut)
async def create_user(user: UserIn):
    return user


# 注意：虽然传入的数据包含 password，但返回时会被自动过滤掉！
# 这就是 response_model 的数据脱敏能力 ✨


# ============================================================
# 二、response_model_exclude / response_model_include
# ============================================================

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
    secret_code: str = "DEFAULT_SECRET"


@app.get("/items/{item_id}", response_model=Item, response_model_exclude={"secret_code"})
async def read_item(item_id: int):
    return {
        "name": "苹果",
        "description": "红富士",
        "price": 5.5,
        "tax": 0.5,
        "secret_code": "SUPER_SECRET_123",
    }


@app.get("/items-public/{item_id}", response_model=Item, response_model_include={"name", "price"})
async def read_item_public(item_id: int):
    return {
        "name": "苹果",
        "description": "红富士",
        "price": 5.5,
        "tax": 0.5,
        "secret_code": "SUPER_SECRET_123",
    }


# ============================================================
# 三、response_model_exclude_unset
# ============================================================
# 只返回实际设置了的字段，不返回默认值字段

class ItemWithDefaults(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: float = 0.0


items_db = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The Bar item", "price": 62, "tax": 20.2},
}


@app.get("/items-unset/{item_id}", response_model=ItemWithDefaults, response_model_exclude_unset=True)
async def read_item_unset(item_id: str):
    return items_db[item_id]


# 访问 /items-unset/foo → 只返回 name 和 price（没有设置 description 和 tax）
# 访问 /items-unset/bar → 返回所有四个字段


# ============================================================
# 四、response_model_exclude_defaults / exclude_none
# ============================================================

@app.get("/items-no-defaults/{item_id}", response_model=ItemWithDefaults, response_model_exclude_defaults=True)
async def read_item_no_defaults(item_id: str):
    return items_db[item_id]


@app.get("/items-no-none/{item_id}", response_model=ItemWithDefaults, response_model_exclude_none=True)
async def read_item_no_none(item_id: str):
    return items_db[item_id]


# ============================================================
# 五、多个响应模型
# ============================================================

class Message(BaseModel):
    message: str


@app.get(
    "/items-multi/{item_id}",
    response_model=Item,
    responses={
        404: {"model": Message, "description": "物品不存在"},
        200: {"description": "成功返回物品信息"},
    },
)
async def read_item_multi(item_id: str):
    if item_id not in items_db:
        return JSONResponse(status_code=404, content={"message": "物品不存在"})
    return items_db[item_id]


# ============================================================
# 六、状态码
# ============================================================

@app.post("/items-status", status_code=201)
async def create_item_status(name: str, price: float):
    return {"name": name, "price": price}


@app.delete("/items-status/{item_id}", status_code=204)
async def delete_item_status(item_id: int):
    return None


# 使用 status 参数指定响应状态码
# 常用状态码：
#   200 - OK（默认）
#   201 - Created（创建成功）
#   204 - No Content（删除成功，无返回内容）
#   400 - Bad Request
#   404 - Not Found
#   422 - Validation Error（FastAPI 自动返回）


# ============================================================
# 七、自定义 Response
# ============================================================

@app.get("/html-response")
async def get_html():
    return HTMLResponse(content="<h1>你好，亲爱的主人！🎀</h1><p>这是 HTML 响应</p>")


@app.get("/text-response")
async def get_text():
    return PlainTextResponse(content="这是纯文本响应～")


@app.get("/json-response")
async def get_json():
    return JSONResponse(
        content={"message": "这是自定义 JSON 响应", "time": datetime.now().isoformat()},
        status_code=200,
        headers={"X-Custom-Header": "Hello from FastAPI"},
    )


# ============================================================
# 八、设置 Cookie 和 Header
# ============================================================

from fastapi import response


@app.post("/cookie-and-header")
async def create_cookie_and_header():
    content = {"message": "Cookie 和 Header 已设置！"}
    response = JSONResponse(content=content)
    response.set_cookie(key="fakesession", value="fake-cookie-session-value")
    response.headers["X-Custom-Header"] = "Custom header value"
    return response


# ============================================================
# 九、Response Model 与类型注解分离
# ============================================================
# 有时候返回类型和 response_model 不同，可以用 -> 注解

@app.get("/user-me", response_model=UserOut)
async def get_current_user() -> UserIn:
    return {
        "username": "admin",
        "password": "secret123",
        "email": "admin@example.com",
    }


# 函数内部返回 UserIn（包含密码），但 response_model=UserOut 会过滤掉密码


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("04_response_model:app", host="127.0.0.1", port=8000, reload=True)
