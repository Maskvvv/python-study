"""
03. 请求体与数据模型 📦
=====================================

亲爱的主人，这节我们学习如何接收和验证请求体数据！
这可是 FastAPI 最强大的地方，结合 Pydantic 简直绝配！
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

app = FastAPI(title="请求体与数据模型")


# ============================================================
# 一、最基本的请求体
# ============================================================

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


@app.post("/items")
async def create_item(item: Item):
    return {
        "item": item,
        "message": f"创建了物品：{item.name}，价格：{item.price}",
        "price_with_tax": item.price + item.tax if item.tax else item.price,
    }


# 请求示例（POST /items，Body 为 JSON）：
# {
#     "name": "苹果",
#     "description": "红富士苹果",
#     "price": 5.5,
#     "tax": 0.5
# }


# ------------------------------------------------------------
# Pydantic 模型的强大之处
# ------------------------------------------------------------
# 1. 自动验证：类型不对直接返回 422 + 清晰的错误信息
# 2. 自动转换：字符串 "5.5" 会自动转成 float 5.5
# 3. 自动文档：Swagger UI 会显示完整的请求体结构
# 4. 模型方法：.model_dump()、.model_dump_json() 等


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, "item": item}


# ============================================================
# 二、用 Field 增加验证规则
# ============================================================

class Product(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, title="产品名称")
    description: Optional[str] = Field(None, max_length=500, title="产品描述")
    price: float = Field(..., gt=0, description="价格必须大于0")
    discount: float = Field(0, ge=0, le=1, description="折扣率 0~1")
    tags: list[str] = Field(default_factory=list, title="标签列表")


@app.post("/products")
async def create_product(product: Product):
    return {
        "product": product,
        "final_price": product.price * (1 - product.discount),
    }


# ============================================================
# 三、嵌套模型
# ============================================================

class Address(BaseModel):
    province: str
    city: str
    street: str
    zip_code: str


class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    age: int = Field(..., ge=0, le=150)
    address: Address
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)


@app.post("/users")
async def create_user(user: User):
    return {
        "user": user,
        "message": f"欢迎 {user.username}，来自 {user.address.city}！"
    }


# 请求示例：
# {
#     "username": "xiaoming",
#     "email": "xiaoming@example.com",
#     "age": 18,
#     "address": {
#         "province": "浙江",
#         "city": "杭州",
#         "street": "西湖大道1号",
#         "zip_code": "310000"
#     }
# }


# ============================================================
# 四、请求体 + 路径参数 + 查询参数
# ============================================================
# 三者可以同时使用！FastAPI 会自动识别：
#   - 路径中 {} 的 → 路径参数
#   - Pydantic 模型类型 → 请求体
#   - 基本类型 + 默认值 → 查询参数

@app.put("/users/{user_id}/items/{item_id}")
async def update_user_item(
    user_id: int,
    item_id: int,
    item: Item,
    q: Optional[str] = None,
):
    result = {"user_id": user_id, "item_id": item_id, "item": item}
    if q:
        result.update({"q": q})
    return result


# ============================================================
# 五、多个请求体参数
# ============================================================

class UserBase(BaseModel):
    username: str
    email: EmailStr


class ItemBase(BaseModel):
    name: str
    price: float


@app.post("/user-with-item")
async def create_user_with_item(user: UserBase, item: ItemBase):
    return {"user": user, "item": item}


# 当有多个请求体参数时，FastAPI 期望这样的 JSON：
# {
#     "user": { "username": "...", "email": "..." },
#     "item": { "name": "...", "price": ... }
# }


# ============================================================
# 六、Body 嵌入单个参数
# ============================================================

from fastapi import Body


@app.post("/item-embed")
async def create_item_embed(item: Item = Body(embed=True)):
    return {"item": item}


# embed=True 时，即使只有一个请求体参数，也需要包裹在 key 中：
# { "item": { "name": "...", "price": ... } }
# 而不是直接：{ "name": "...", "price": ... }


# ============================================================
# 七、模型继承与复用
# ============================================================

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    username: str
    email: EmailStr
    is_active: bool = True


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3)
    email: Optional[EmailStr] = None


# 创建时用 UserCreate（需要密码）
# 返回时用 UserResponse（不包含密码）
# 更新时用 UserUpdate（所有字段可选）


@app.post("/users-safe", response_model=UserResponse)
async def create_user_safe(user: UserCreate):
    return user


@app.patch("/users-safe/{user_id}", response_model=UserResponse)
async def update_user_safe(user_id: int, user: UserUpdate):
    return {"user_id": user_id, **user.model_dump(exclude_unset=True)}


# ============================================================
# 八、模型配置
# ============================================================

class ConfigItem(BaseModel):
    name: str
    price: float

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "苹果",
                    "price": 5.5,
                }
            ]
        }
    }


@app.post("/config-items")
async def create_config_item(item: ConfigItem):
    return item


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("03_request_body:app", host="127.0.0.1", port=8000, reload=True)
