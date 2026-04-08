from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "your_secret_key_here"


@app.route("/")
def index():
    return render_template("index.html", title="首页", message="欢迎来到 Flask 模板世界！🎉")


@app.route("/user/<name>")
def user(name):
    return render_template("user.html", name=name, title=f"用户 - {name}")


@app.route("/loop")
def loop_demo():
    items = ["Python", "Flask", "Jinja2", "HTML", "CSS"]
    return render_template("loop.html", items=items, title="循环示例")


@app.route("/condition/<int:score>")
def condition_demo(score):
    return render_template("condition.html", score=score, title="条件示例")


@app.route("/form", methods=["GET", "POST"])
def form_demo():
    if request.method == "POST":
        username = request.form.get("username", "")
        email = request.form.get("email", "")
        if not username:
            flash("用户名不能为空！", "error")
        else:
            flash(f"提交成功！欢迎 {username} 🎊", "success")
            return redirect(url_for("form_demo"))
    return render_template("form.html", title="表单示例")


if __name__ == "__main__":
    app.run(debug=True, port=5002)
