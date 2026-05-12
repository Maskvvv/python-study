"""
06. 安全与认证 🔐
=====================================

亲爱的主人，安全很重要哦！这节我们来学习 FastAPI 的安全功能～
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.routing import APIRoute
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import hashlib

app = FastAPI(title="安全与认证")


# ============================================================
# 一、最简单的认证：API Key
# ============================================================

from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")


async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != "my-secret-api-key":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return api_key


@app.get("/protected")
async def protected_route(api_key: str = Depends(verify_api_key)):
    return {"message": "你通过了认证！", "api_key": api_key}


# 访问时需要在 Header 中添加：X-API-Key: my-secret-api-key


# ============================================================
# 二、OAuth2 密码模式（最常用！）
# ============================================================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# 模拟用户数据库
fake_users_db = {
    "alice": {
        "username": "alice",
        "hashed_password": hashlib.sha256("secret".encode()).hexdigest(),
        "email": "alice@example.com",
        "disabled": False,
    },
    "bob": {
        "username": "bob",
        "hashed_password": hashlib.sha256("secret2".encode()).hexdigest(),
        "email": "bob@example.com",
        "disabled": True,
    },
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    email: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


def get_user(db: dict, username: str) -> Optional[UserInDB]:
    if username in db:
        return UserInDB(**db[username])
    return None


def fake_hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate_user(db: dict, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not fake_hash_password(password) == user.hashed_password:
        return False
    return user


# ------------------------------------------------------------
# 生成 Token（简化版，实际项目用 python-jose）
# ------------------------------------------------------------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire.isoformat()})
    fake_token = hashlib.sha256(str(to_encode).encode()).hexdigest()
    return fake_token


# ------------------------------------------------------------
# Token 端点
# ------------------------------------------------------------

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# ------------------------------------------------------------
# 获取当前用户
# ------------------------------------------------------------

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # 简化版：实际项目需要解码 JWT token
    for username, user_data in fake_users_db.items():
        return User(**user_data)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user


# ------------------------------------------------------------
# 受保护的路由
# ------------------------------------------------------------

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/users/me/items")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": 1, "owner": current_user.username}]


# ============================================================
# 三、Swagger UI 中的认证
# ============================================================
# 访问 /docs 页面，右上角有一个 🔓 Authorize 按钮
# 点击后输入用户名和密码，之后所有请求都会自动带上 Token
#
# 测试步骤：
#   1. 访问 http://127.0.0.1:8000/docs
#   2. 点击 Authorize 按钮
#   3. 输入用户名 alice，密码 secret
#   4. 点击 Authorize 确认
#   5. 现在可以调用 /users/me 了


# ============================================================
# 四、生产环境建议
# ============================================================
"""
实际项目中，你应该使用：

1. JWT Token（推荐）
   pip install python-jose[cryptography]
   用 jose.jwt.encode() / decode() 生成和验证 token

2. 密码哈希（推荐）
   pip install passlib[bcrypt]
   用 passlib.hash.bcrypt 来哈希密码

3. 完整示例：
   from jose import jwt
   from passlib.context import CryptContext

   SECRET_KEY = "your-secret-key-keep-it-safe"
   ALGORITHM = "HS256"

   pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

   def create_access_token(data: dict):
       return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

   def verify_password(plain_password, hashed_password):
       return pwd_context.verify(plain_password, hashed_password)

   def get_password_hash(password):
       return pwd_context.hash(password)
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("06_security_auth:app", host="127.0.0.1", port=8000, reload=True)
