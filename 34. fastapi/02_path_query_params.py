"""
02. 路径参数与查询参数 🔍
=====================================

亲爱的主人，这节我们来学习 FastAPI 中最核心的参数传递方式！
"""

from fastapi import FastAPI
from enum import Enum

app = FastAPI(title="路径参数与查询参数")


# ============================================================
# 一、路径参数（Path Parameters）
# ============================================================
# 路径参数是 URL 路径的一部分，用 {} 包裹

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id, "message": f"获取用户 {user_id} 的信息"}


# 路径参数的类型注解会自动：
#   1. 验证数据类型（传非整数会返回 422 错误）
#   2. 在 API 文档中标注类型
#   3. 自动转换数据类型（字符串 "123" → 整数 123）


# ------------------------------------------------------------
# 多个路径参数
# ------------------------------------------------------------

@app.get("/users/{user_id}/posts/{post_id}")
async def get_user_post(user_id: int, post_id: int):
    return {
        "user_id": user_id,
        "post_id": post_id,
        "message": f"用户 {user_id} 的第 {post_id} 篇文章"
    }


# ------------------------------------------------------------
# 路径参数与枚举
# ------------------------------------------------------------
# 如果参数只能是几个固定值，可以用 Enum

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    vgg = "vgg"


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model": model_name, "message": "Deep Learning AlexNet!"}
    if model_name is ModelName.resnet:
        return {"model": model_name, "message": "Deep Learning ResNet!"}
    return {"model": model_name, "message": "Deep Learning VGG!"}


# ------------------------------------------------------------
# 路径参数包含路径（file_path）
# ------------------------------------------------------------
# 如果路径参数本身包含 /，需要用 Path 类型

from fastapi import Path

@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


# ============================================================
# 二、查询参数（Query Parameters）
# ============================================================
# 查询参数是 URL 中 ? 后面的部分
# 例如：/items?skip=0&limit=10

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


@app.get("/items")
async def read_items(skip: int = 0, limit: int = 10):
    return fake_items_db[skip: skip + limit]


# 访问示例：
#   /items              → skip=0, limit=10（使用默认值）
#   /items?skip=1       → skip=1, limit=10
#   /items?skip=0&limit=2 → skip=0, limit=2


# ------------------------------------------------------------
# 可选查询参数
# ------------------------------------------------------------

from typing import Optional

@app.get("/items/{item_id}")
async def read_item(item_id: str, q: Optional[str] = None):
    result = {"item_id": item_id}
    if q:
        result.update({"q": q})
    return result


# 访问示例：
#   /items/abc           → {"item_id": "abc"}
#   /items/abc?q=hello   → {"item_id": "abc", "q": "hello"}


# ------------------------------------------------------------
# 查询参数类型转换
# ------------------------------------------------------------

@app.get("/items-bool/{item_id}")
async def read_item_bool(item_id: str, short: bool = False):
    item = {"item_id": item_id}
    if not short:
        item.update({"description": "这是一段很长的描述..."})
    return item


# 访问示例：
#   /items-bool/1             → 有 description
#   /items-bool/1?short=true  → 没有 description
#   /items-bool/1?short=1     → 没有 description（1=True, 0=False）


# ------------------------------------------------------------
# 必填查询参数
# ------------------------------------------------------------
# 没有默认值的参数就是必填的

@app.get("/required-query")
async def required_query(needy: str):
    return {"needy": needy}


# 访问 /required-query 会返回 422 错误（缺少 needy 参数）
# 访问 /required-query?needy=hello 才能正常返回


# ============================================================
# 三、参数验证与元数据
# ============================================================

from fastapi import Query


@app.get("/items-validated")
async def read_items_validated(
    q: Optional[str] = Query(
        None,
        title="查询字符串",
        description="用于搜索物品的查询字符串",
        min_length=3,
        max_length=50,
    ),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的最大记录数"),
):
    results = {
        "skip": skip,
        "limit": limit,
    }
    if q:
        results.update({"q": q})
    return results


# Query 验证参数说明：
#   min_length / max_length  → 字符串长度限制
#   ge (greater or equal)   → 最小值
#   le (less or equal)      → 最大值
#   gt (greater than)       → 严格大于
#   lt (less than)          → 严格小于
#   title / description     → API 文档中的说明


# ============================================================
# 四、路径参数验证
# ============================================================

@app.get("/items-path/{item_id}")
async def read_items_path(
    item_id: int = Path(
        ...,
        title="物品ID",
        description="物品的唯一标识符",
        ge=1,
        le=1000,
    )
):
    return {"item_id": item_id}


# Path(...) 中的 ... 表示必填参数


# ============================================================
# 五、参数顺序小技巧
# ============================================================
# Python 要求有默认值的参数必须在没有默认值的参数后面
# 但 FastAPI 不关心参数顺序！它通过参数名来识别类型
#
# 所以这样写也是可以的：
# @app.get("/items/{item_id}")
# async def read_item(q: str, item_id: int):
#     ...
# FastAPI 知道 item_id 是路径参数，q 是查询参数


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("02_path_query_params:app", host="127.0.0.1", port=8000, reload=True)
