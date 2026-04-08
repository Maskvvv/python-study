import os
from flask import Flask, request, redirect, url_for, flash, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "upload_secret_key"
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return """
    <h1>文件上传示例 📁</h1>
    <form method="post" enctype="multipart/form-data" action="/upload">
        <input type="file" name="file" required>
        <button type="submit">上传文件</button>
    </form>
    <p>允许的文件类型: txt, pdf, png, jpg, jpeg, gif</p>
    <p>最大文件大小: 16MB</p>
    """


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "<h2>没有选择文件 ❌</h2><a href='/'>返回</a>"

    file = request.files["file"]

    if file.filename == "":
        return "<h2>没有选择文件 ❌</h2><a href='/'>返回</a>"

    if file and allowed_file(file.filename):
        if not os.path.exists(app.config["UPLOAD_FOLDER"]):
            os.makedirs(app.config["UPLOAD_FOLDER"])

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        return f"""
        <h2>文件上传成功！✅</h2>
        <p>文件名: {filename}</p>
        <p>保存路径: {filepath}</p>
        <a href='/'>继续上传</a>
        """
    else:
        return "<h2>不允许的文件类型 ❌</h2><a href='/'>返回</a>"


if __name__ == "__main__":
    app.run(debug=True, port=5004)
