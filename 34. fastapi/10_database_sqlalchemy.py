"""
10. 数据库集成 SQLAlchemy 🗄️
=====================================

亲爱的主人，这节我们学习如何把 FastAPI 和数据库连接起来！
SQLAlchemy 是 Python 最强大的 ORM 之一～
"""

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from datetime import datetime

app = FastAPI(title="数据库集成 SQLAlchemy")


# ============================================================
# 一、数据库配置
# ============================================================
# 这里用 SQLite 做演示（不需要额外安装数据库服务）
# 生产环境可以换成 PostgreSQL / MySQL

SQLALCHEMY_DATABASE_URL = "sqlite:///./fastapi_demo.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# ============================================================
# 二、定义 ORM 模型
# ============================================================

class TodoModel(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# 创建数据库表
Base.metadata.create_all(bind=engine)


# ============================================================
# 三、Pydantic 模型（用于 API 请求/响应）
# ============================================================

class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    completed: Optional[bool] = None


class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# 四、数据库会话依赖
# ============================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================
# 五、CRUD 操作
# ============================================================

@app.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = TodoModel(**todo.model_dump())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


@app.get("/todos", response_model=List[TodoResponse])
async def list_todos(
    skip: int = 0,
    limit: int = 100,
    completed: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    query = db.query(TodoModel)
    if completed is not None:
        query = query.filter(TodoModel.completed == completed)
    return query.offset(skip).limit(limit).all()


@app.get("/todos/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo 不存在")
    return todo


@app.put("/todos/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: int, todo: TodoUpdate, db: Session = Depends(get_db)):
    db_todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo 不存在")

    update_data = todo.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_todo, key, value)

    db.commit()
    db.refresh(db_todo)
    return db_todo


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo 不存在")
    db.delete(db_todo)
    db.commit()


# ============================================================
# 六、搜索功能
# ============================================================

@app.get("/todos-search", response_model=List[TodoResponse])
async def search_todos(q: str, db: Session = Depends(get_db)):
    results = db.query(TodoModel).filter(
        TodoModel.title.contains(q) | TodoModel.description.contains(q)
    ).all()
    return results


# ============================================================
# 七、统计接口
# ============================================================

from sqlalchemy import func


class TodoStats(BaseModel):
    total: int
    completed: int
    pending: int


@app.get("/todos-stats", response_model=TodoStats)
async def todo_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(TodoModel.id)).scalar()
    completed = db.query(func.count(TodoModel.id)).filter(TodoModel.completed == True).scalar()
    return TodoStats(total=total, completed=completed, pending=total - completed)


# ============================================================
# 八、异步数据库（生产推荐）
# ============================================================
"""
上面的代码用的是同步 SQLAlchemy，适合入门理解。
生产环境推荐用异步版本：

pip install sqlalchemy[asyncio] aiosqlite

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine("sqlite+aiosqlite:///./async_demo.db")

async def get_db():
    async with AsyncSession(engine) as session:
        yield session

# 查询时用 await：
# result = await db.execute(select(TodoModel))
# todos = result.scalars().all()
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("10_database_sqlalchemy:app", host="127.0.0.1", port=8000, reload=True)
