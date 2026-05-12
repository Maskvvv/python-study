"""
08. 文件上传与静态文件 📁
=====================================

亲爱的主人，这节我们学习如何处理文件上传和提供静态文件服务！
"""

import html
from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import os
import shutil

app = FastAPI(title="文件上传与静态文件")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============================================================
# 一、File 类型 - 最简单的文件上传
# ============================================================

@app.post("/upload-file")
async def upload_file(file: bytes = File(...)):
    return {
        "file_size": len(file),
        "message": f"收到了 {len(file)} 字节的文件",
    }


# File(...) 接收整个文件为 bytes
# 适合小文件，因为整个文件会加载到内存


# ============================================================
# 二、UploadFile 类型 - 推荐方式！
# ============================================================

@app.post("/upload-file-better")
async def upload_file_better(file: UploadFile):
    file_location = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": os.path.getsize(file_location),
        "message": f"文件 {file.filename} 已保存！",
    }


# UploadFile 的优势：
#   1. 不会全部加载到内存，适合大文件
#   2. 有 filename、content_type 等元信息
#   3. 有 file 属性（类文件对象），可以流式读取
#   4. 支持 async：await file.read()、await file.write()


# ============================================================
# 三、多文件上传
# ============================================================

@app.post("/upload-multiple")
async def upload_multiple(files: List[UploadFile]):
    results = []
    for file in files:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)
        results.append({
            "filename": file.filename,
            "size": os.path.getsize(file_location),
        })
    return {"uploaded_files": results, "count": len(files)}


# ============================================================
# 四、带表单字段的文件上传
# ============================================================

from fastapi import Form

@app.post("/upload-with-form")
async def upload_with_form(
    file: UploadFile,
    description: str = Form(...),
    category: str = Form("general"),
):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {
        "filename": file.filename,
        "description": description,
        "category": category,
        "message": "文件和表单数据都收到了！",
    }


# ============================================================
# 五、文件下载
# ============================================================

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream",
    )


# ============================================================
# 六、列出已上传的文件
# ============================================================

@app.get("/files")
async def list_files():
    files = []
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        files.append({
            "filename": filename,
            "size": os.path.getsize(file_path),
        })
    return {"files": files, "count": len(files)}


# ============================================================
# 七、删除文件
# ============================================================

@app.delete("/files/{filename}")
async def delete_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    os.remove(file_path)
    return {"message": f"文件 {filename} 已删除"}


# ============================================================
# 八、文件大小限制
# ============================================================
# 可以通过中间件限制请求体大小

from fastapi import Request

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@app.middleware("http")
async def limit_upload_size(request: Request, call_next):
    if request.method == "POST" and "/upload" in request.url.path:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_FILE_SIZE:
            return JSONResponse(  # noqa: F821
                status_code=413,
                content={"detail": f"文件太大，最大允许 {MAX_FILE_SIZE // 1024 // 1024}MB"},
            )
    return await call_next(request)


# ============================================================
# 九、静态文件服务
# ============================================================
# 如果需要提供静态文件目录，可以这样：

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

STATIC_DIR = "static"
os.makedirs(STATIC_DIR, exist_ok=True)


@app.get("/static", response_class=HTMLResponse)
async def list_static_files():
    files = os.listdir(STATIC_DIR)
    links = "".join(
        f'<li><a href="/static/{f}">{f}</a></li>' for f in files
    )
    return f"<h2>Static Files</h2><ul>{links}</ul>" if links else "<h2>Static Files</h2><p>目录为空</p>"


app.mount("/static", StaticFiles(directory=STATIC_DIR, html=True), name="static")


# ============================================================
# 十、图片上传与预览
# ============================================================

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


@app.post("/upload-image")
async def upload_image(file: UploadFile):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的图片类型：{file.content_type}，支持：{ALLOWED_IMAGE_TYPES}",
        )

    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "preview_url": f"/download/{file.filename}",
        "message": "图片上传成功！",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("08_file_upload_static:app", host="127.0.0.1", port=8000, reload=True)
