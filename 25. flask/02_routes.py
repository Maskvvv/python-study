from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return "这是首页 🏠"


@app.route("/user/<username>")
def show_user_profile(username):
    return f"用户主页：{username} 👤"


@app.route("/post/<int:post_id>")
def show_post(post_id):
    return f"文章编号：{post_id} 📄"


@app.route("/path/<path:subpath>")
def show_subpath(subpath):
    return f"子路径：{subpath} 🛤️"


@app.route("/projects/")
def projects():
    return "项目页面（结尾有斜杠，访问时可以省略）📁"


@app.route("/about")
def about():
    return "关于页面（结尾无斜杠，访问时不能加斜杠）📖"


@app.route("/login", methods=["GET", "POST"])
def login():
    if True:
        return "GET 请求 - 显示登录表单 🔐"
    else:
        return "POST 请求 - 处理登录数据 🚀"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
