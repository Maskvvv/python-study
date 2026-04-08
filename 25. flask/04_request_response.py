from flask import Flask, request, make_response, jsonify, session

app = Flask(__name__)
app.secret_key = "super_secret_key_123"


@app.route("/")
def index():
    return """
    <h1>请求与响应示例</h1>
    <ul>
        <li><a href="/request_info">查看请求信息</a></li>
        <li><a href="/cookie_demo">Cookie 示例</a></li>
        <li><a href="/session_demo">Session 示例</a></li>
        <li><a href="/json_demo">JSON 响应示例</a></li>
        <li><a href="/custom_header">自定义响应头</a></li>
    </ul>
    """


@app.route("/request_info")
def request_info():
    info = {
        "请求方法": request.method,
        "请求路径": request.path,
        "完整URL": request.url,
        "客户端IP": request.remote_addr,
        "User-Agent": request.headers.get("User-Agent", "未知"),
        "查询参数": dict(request.args),
    }
    html = "<h2>请求信息 📋</h2><ul>"
    for key, value in info.items():
        html += f"<li><strong>{key}:</strong> {value}</li>"
    html += "</ul><a href='/'>返回首页</a>"
    return html


@app.route("/cookie_demo")
def cookie_demo():
    resp = make_response("<h2>Cookie 已设置！🍪</h2><a href='/show_cookie'>查看 Cookie</a>")
    resp.set_cookie("username", "dear_master", max_age=60 * 60 * 24)
    resp.set_cookie("theme", "dark", max_age=60 * 60 * 24)
    return resp


@app.route("/show_cookie")
def show_cookie():
    username = request.cookies.get("username", "未设置")
    theme = request.cookies.get("theme", "未设置")
    return f"""
    <h2>Cookie 信息 🍪</h2>
    <p>用户名: {username}</p>
    <p>主题: {theme}</p>
    <a href='/'>返回首页</a>
    """


@app.route("/session_demo")
def session_demo():
    if "visits" not in session:
        session["visits"] = 0
    session["visits"] += 1
    return f"""
    <h2>Session 示例 🗝️</h2>
    <p>这是你第 {session['visits']} 次访问此页面</p>
    <p><a href='/clear_session'>清除 Session</a></p>
    <a href='/'>返回首页</a>
    """


@app.route("/clear_session")
def clear_session():
    session.clear()
    return "<h2>Session 已清除！✨</h2><a href='/session_demo'>重新开始</a>"


@app.route("/json_demo")
def json_demo():
    data = {
        "message": "这是一个 JSON 响应",
        "status": "success",
        "data": {"name": "Flask", "version": "3.1.3", "emoji": "🐍"},
    }
    return jsonify(data)


@app.route("/custom_header")
def custom_header():
    resp = make_response("<h2>这个响应带有自定义头部！🎯</h2>")
    resp.headers["X-Custom-Header"] = "Hello from Flask"
    resp.headers["X-Author"] = "Dear Master"
    return resp


if __name__ == "__main__":
    app.run(debug=True, port=5003)
