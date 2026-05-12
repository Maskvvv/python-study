"""
14. 后台任务与长时AI任务 ⏳
=====================================

亲爱的主人，AI 任务通常很耗时，不能让用户一直等着！
后台任务 + 状态查询 是解决这个问题的标准方案～
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
import asyncio
import json
import uuid
import time
from datetime import datetime

app = FastAPI(title="后台任务与长时AI任务")

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


# ============================================================
# 一、BackgroundTasks 基础
# ============================================================
# FastAPI 内置的后台任务功能
# 在响应返回之后执行，不阻塞用户

def send_email_notification(email: str, message: str):
    print(f"  📧 发送邮件给 {email}: {message}")
    time.sleep(2)
    print(f"  ✅ 邮件发送完成")


class NotificationRequest(BaseModel):
    email: str
    message: str


@app.post("/notify")
async def send_notification(request: NotificationRequest, bg_tasks: BackgroundTasks):
    bg_tasks.add_task(send_email_notification, request.email, request.message)
    return {"message": "通知已加入后台队列，马上发送！"}


# 用户立即收到响应，邮件在后台发送


# ============================================================
# 二、多个后台任务
# ============================================================

def log_request(request_id: str):
    print(f"  📝 记录请求日志: {request_id}")


def update_stats(request_id: str):
    print(f"  📊 更新统计数据: {request_id}")


@app.post("/multi-bg-tasks")
async def multi_bg_tasks(bg_tasks: BackgroundTasks):
    request_id = str(uuid.uuid4())[:8]
    bg_tasks.add_task(log_request, request_id)
    bg_tasks.add_task(update_stats, request_id)
    return {"request_id": request_id, "message": "后台任务已加入队列"}


# ============================================================
# 三、任务状态管理（核心！）
# ============================================================
# 对于长时间运行的 AI 任务，我们需要：
#   1. 提交任务 → 返回任务 ID
#   2. 查询状态 → 用 ID 查进度
#   3. 获取结果 → 任务完成后拿结果

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskInfo(BaseModel):
    task_id: str
    status: TaskStatus
    progress: float = 0
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


tasks_db: dict[str, TaskInfo] = {}


async def run_ai_task(task_id: str, prompt: str, steps: int = 10):
    """模拟一个耗时的 AI 任务"""
    try:
        tasks_db[task_id].status = TaskStatus.RUNNING
        tasks_db[task_id].updated_at = datetime.now()

        result_parts = []
        for i in range(steps):
            await asyncio.sleep(1)
            progress = (i + 1) / steps * 100
            tasks_db[task_id].progress = progress
            tasks_db[task_id].updated_at = datetime.now()
            result_parts.append(f"步骤{i + 1}完成。")

        tasks_db[task_id].status = TaskStatus.COMPLETED
        tasks_db[task_id].progress = 100
        tasks_db[task_id].result = f"AI 对「{prompt}」的分析结果：\n" + "\n".join(result_parts)
        tasks_db[task_id].updated_at = datetime.now()

    except Exception as e:
        tasks_db[task_id].status = TaskStatus.FAILED
        tasks_db[task_id].error = str(e)
        tasks_db[task_id].updated_at = datetime.now()


class AITaskRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="AI 任务描述")
    steps: int = Field(5, ge=1, le=20, description="模拟步骤数")


@app.post("/ai-tasks", response_model=TaskInfo)
async def create_ai_task(request: AITaskRequest, bg_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())[:8]
    task_info = TaskInfo(
        task_id=task_id,
        status=TaskStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    tasks_db[task_id] = task_info

    bg_tasks.add_task(run_ai_task, task_id, request.prompt, request.steps)

    return task_info


@app.get("/ai-tasks/{task_id}", response_model=TaskInfo)
async def get_task_status(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="任务不存在")
    return tasks_db[task_id]


@app.get("/ai-tasks", response_model=list[TaskInfo])
async def list_tasks(status: Optional[TaskStatus] = None):
    tasks = list(tasks_db.values())
    if status:
        tasks = [t for t in tasks if t.status == status]
    return tasks


@app.delete("/ai-tasks/{task_id}")
async def delete_task(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="任务不存在")
    del tasks_db[task_id]
    return {"message": f"任务 {task_id} 已删除"}


# ============================================================
# 四、任务进度 SSE 推送
# ============================================================
# 提交任务后，通过 SSE 实时推送进度

@app.get("/ai-tasks/{task_id}/progress")
async def stream_task_progress(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="任务不存在")

    async def event_stream():
        while True:
            task = tasks_db[task_id]
            data = json.dumps({
                "status": task.status.value,
                "progress": task.progress,
                "result": task.result,
                "error": task.error,
            }, ensure_ascii=False)
            yield f"data: {data}\n\n"

            if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                break

            await asyncio.sleep(0.5)

    return StreamingResponse(event_stream(), media_type="text/event-stream", headers=SSE_HEADERS)


# ============================================================
# 五、并发控制
# ============================================================
# 限制同时运行的 AI 任务数量

MAX_CONCURRENT_TASKS = 3
task_semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)


async def run_ai_task_limited(task_id: str, prompt: str, steps: int = 5):
    async with task_semaphore:
        await run_ai_task(task_id, prompt, steps)


@app.post("/ai-tasks-limited", response_model=TaskInfo)
async def create_limited_task(request: AITaskRequest, bg_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())[:8]
    task_info = TaskInfo(
        task_id=task_id,
        status=TaskStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    tasks_db[task_id] = task_info

    bg_tasks.add_task(run_ai_task_limited, task_id, request.prompt, request.steps)

    return task_info


# ============================================================
# 六、任务超时处理
# ============================================================

async def run_ai_task_with_timeout(task_id: str, prompt: str, timeout: float = 30.0):
    try:
        tasks_db[task_id].status = TaskStatus.RUNNING
        tasks_db[task_id].updated_at = datetime.now()

        result = await asyncio.wait_for(
            _simulate_ai_work(prompt),
            timeout=timeout,
        )

        tasks_db[task_id].status = TaskStatus.COMPLETED
        tasks_db[task_id].progress = 100
        tasks_db[task_id].result = result
        tasks_db[task_id].updated_at = datetime.now()

    except asyncio.TimeoutError:
        tasks_db[task_id].status = TaskStatus.FAILED
        tasks_db[task_id].error = f"任务超时（{timeout}秒）"
        tasks_db[task_id].updated_at = datetime.now()
    except Exception as e:
        tasks_db[task_id].status = TaskStatus.FAILED
        tasks_db[task_id].error = str(e)
        tasks_db[task_id].updated_at = datetime.now()


async def _simulate_ai_work(prompt: str) -> str:
    await asyncio.sleep(5)
    return f"AI 对「{prompt}」的分析已完成！"


class TimeoutTaskRequest(BaseModel):
    prompt: str
    timeout: float = Field(30, ge=5, le=300, description="超时时间（秒）")


@app.post("/ai-tasks-timeout", response_model=TaskInfo)
async def create_timeout_task(request: TimeoutTaskRequest, bg_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())[:8]
    task_info = TaskInfo(
        task_id=task_id,
        status=TaskStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    tasks_db[task_id] = task_info

    bg_tasks.add_task(run_ai_task_with_timeout, task_id, request.prompt, request.timeout)

    return task_info


# ============================================================
# 七、任务管理前端页面
# ============================================================

task_html = """
<!DOCTYPE html>
<html>
<head>
    <title>AI 任务管理 ⏳</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 700px; margin: 30px auto; padding: 0 20px; }
        .box { border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 10px 0; }
        .task { border-left: 4px solid #007bff; padding: 10px; margin: 8px 0; background: #f8f9fa; border-radius: 4px; }
        .task.completed { border-left-color: #28a745; }
        .task.failed { border-left-color: #dc3545; }
        .task.running { border-left-color: #ffc107; }
        .progress-bar { width: 100%; height: 8px; background: #e9ecef; border-radius: 4px; margin-top: 5px; }
        .progress-fill { height: 100%; background: #007bff; border-radius: 4px; transition: width 0.3s; }
        .btn { padding: 8px 16px; margin: 5px; cursor: pointer; border: none; border-radius: 4px; background: #007bff; color: white; }
        .btn:hover { background: #0056b3; }
        input, textarea { padding: 8px; border: 1px solid #ddd; border-radius: 4px; width: 100%; box-sizing: border-box; }
        .status { font-size: 12px; color: #6c757d; }
    </style>
</head>
<body>
    <h1>⏳ AI 任务管理</h1>

    <div class="box">
        <h3>创建新任务</h3>
        <textarea id="prompt" rows="2" placeholder="输入AI任务描述...">分析这段文本的情感倾向</textarea>
        <div style="margin-top:10px;">
            <label>步骤数：<input id="steps" type="number" value="5" min="1" max="20" style="width:80px;" /></label>
            <button class="btn" onclick="createTask()">提交任务</button>
        </div>
    </div>

    <div class="box">
        <h3>任务列表</h3>
        <button class="btn" onclick="refreshTasks()" style="margin-bottom:10px;">刷新</button>
        <div id="tasks"></div>
    </div>

    <script>
        async function createTask() {
            const prompt = document.getElementById("prompt").value;
            const steps = parseInt(document.getElementById("steps").value);
            const res = await fetch("/ai-tasks", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt, steps }),
            });
            const task = await res.json();
            watchTask(task.task_id);
            refreshTasks();
        }

        async function refreshTasks() {
            const res = await fetch("/ai-tasks");
            const tasks = await res.json();
            const container = document.getElementById("tasks");
            container.innerHTML = tasks.length === 0 ? "<p class='status'>暂无任务</p>" : "";
            tasks.reverse().forEach(t => {
                container.innerHTML += `
                    <div class="task ${t.status}">
                        <strong>${t.task_id}</strong> - ${t.status}
                        (${t.progress.toFixed(0)}%)
                        <div class="progress-bar"><div class="progress-fill" style="width:${t.progress}%"></div></div>
                        <div class="status">${t.prompt || ''} | ${t.updated_at}</div>
                        ${t.result ? '<div style="margin-top:5px;white-space:pre-wrap;">' + t.result + '</div>' : ''}
                        ${t.error ? '<div style="color:red;margin-top:5px;">' + t.error + '</div>' : ''}
                    </div>
                `;
            });
        }

        function watchTask(taskId) {
            const es = new EventSource(`/ai-tasks/${taskId}/progress`);
            es.onmessage = (e) => {
                const data = JSON.parse(e.data);
                if (data.status === "completed" || data.status === "failed") {
                    es.close();
                    refreshTasks();
                } else {
                    refreshTasks();
                }
            };
        }

        refreshTasks();
    </script>
</body>
</html>
"""


@app.get("/tasks-page")
async def tasks_page():
    return task_html


# ============================================================
# 八、生产环境：Celery 集成
# ============================================================
"""
当任务量变大时，BackgroundTasks 就不够用了。
生产环境推荐用 Celery + Redis/RabbitMQ：

┌──────────┐     ┌──────────┐     ┌──────────┐
│ FastAPI  │────→│  Redis   │────→│  Celery  │
│ (Web)    │     │ (Broker) │     │ (Worker) │
└──────────┘     └──────────┘     └──────────┘
     │                                    │
     │←───── 结果查询 ←──────────────────│
     └──────────┐     ┌──────────┘
                │     │
                └─ Redis (Backend)

优点：
  1. 任务持久化，重启不丢失
  2. 分布式 Worker，水平扩展
  3. 任务重试、定时任务
  4. 任务优先级、路由
  5. 完善的监控（Flower）

示例代码：
  from celery import Celery

  celery_app = Celery("worker", broker="redis://localhost:6379/0")

  @celery_app.task
  def ai_task(prompt: str):
      ...  # 耗时 AI 操作

  # FastAPI 中调用
  @app.post("/tasks")
  async def create_task(prompt: str):
      task = ai_task.delay(prompt)
      return {"task_id": task.id}
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("14_background_tasks:app", host="127.0.0.1", port=8000, reload=True)
