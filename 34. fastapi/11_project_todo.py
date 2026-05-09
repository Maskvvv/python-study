"""
11. 实战项目：Todo API 📝
=====================================

亲爱的主人，这是我们的实战项目！
把前面学到的所有知识综合起来，做一个完整的 Todo API！
"""

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from datetime import datetime

app = FastAPI(
    title="Todo API",
    description="一个完整的 Todo API 实战项目",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 数据库配置
# ============================================================

engine = create_engine("sqlite:///./todo_app.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============================================================
# ORM 模型
# ============================================================

class TodoModel(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    completed = Column(Boolean, default=False)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


Base.metadata.create_all(bind=engine)


# ============================================================
# Pydantic 模型
# ============================================================

class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="任务标题")
    description: Optional[str] = Field(None, max_length=500, description="任务描述")
    priority: int = Field(0, ge=0, le=5, description="优先级 0-5")


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    completed: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=0, le=5)


class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool
    priority: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TodoStats(BaseModel):
    total: int
    completed: int
    pending: int
    avg_priority: float


class Message(BaseModel):
    message: str


# ============================================================
# 依赖
# ============================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class PaginationParams:
    def __init__(self, page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
        self.page = page
        self.page_size = page_size
        self.skip = (page - 1) * page_size
        self.limit = page_size


# ============================================================
# API 路由
# ============================================================

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "🎀 欢迎使用 Todo API！",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED, tags=["Todos"])
async def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = TodoModel(**todo.model_dump())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


@app.get("/todos", response_model=List[TodoResponse], tags=["Todos"])
async def list_todos(
    pagination: PaginationParams = Depends(),
    completed: Optional[bool] = None,
    priority: Optional[int] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(TodoModel)

    if completed is not None:
        query = query.filter(TodoModel.completed == completed)
    if priority is not None:
        query = query.filter(TodoModel.priority == priority)
    if q:
        query = query.filter(TodoModel.title.contains(q) | TodoModel.description.contains(q))

    return query.order_by(TodoModel.priority.desc()).offset(pagination.skip).limit(pagination.limit).all()


@app.get("/todos/{todo_id}", response_model=TodoResponse, tags=["Todos"])
async def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo {todo_id} 不存在")
    return todo


@app.put("/todos/{todo_id}", response_model=TodoResponse, tags=["Todos"])
async def update_todo(todo_id: int, todo: TodoUpdate, db: Session = Depends(get_db)):
    db_todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail=f"Todo {todo_id} 不存在")

    update_data = todo.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_todo, key, value)

    db.commit()
    db.refresh(db_todo)
    return db_todo


@app.delete("/todos/{todo_id}", response_model=Message, tags=["Todos"])
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail=f"Todo {todo_id} 不存在")
    db.delete(db_todo)
    db.commit()
    return {"message": f"Todo {todo_id} 已删除"}


@app.patch("/todos/{todo_id}/toggle", response_model=TodoResponse, tags=["Todos"])
async def toggle_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail=f"Todo {todo_id} 不存在")
    db_todo.completed = not db_todo.completed
    db.commit()
    db.refresh(db_todo)
    return db_todo


@app.get("/todos-stats", response_model=TodoStats, tags=["Stats"])
async def todo_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(TodoModel.id)).scalar()
    completed = db.query(func.count(TodoModel.id)).filter(TodoModel.completed == True).scalar()
    avg_priority = db.query(func.avg(TodoModel.priority)).scalar() or 0
    return TodoStats(total=total, completed=completed, pending=total - completed, avg_priority=round(avg_priority, 2))


@app.delete("/todos-completed", response_model=Message, tags=["Todos"])
async def delete_completed_todos(db: Session = Depends(get_db)):
    count = db.query(TodoModel).filter(TodoModel.completed == True).delete()
    db.commit()
    return {"message": f"已删除 {count} 个已完成的 Todo"}


# ============================================================
# 运行
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("11_project_todo:app", host="127.0.0.1", port=8000, reload=True)
