from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return """
    <h1>Flask 学习路线图 🗺️</h1>
    <ol>
        <li><a href="http://localhost:5000">01_hello.py - Hello Flask 基础入门</a></li>
        <li><a href="http://localhost:5001">02_routes.py - 路由与URL规则</a></li>
        <li><a href="http://localhost:5002">03_templates.py - 模板渲染</a></li>
        <li><a href="http://localhost:5003">04_request_response.py - 请求与响应</a></li>
        <li><a href="http://localhost:5004">05_file_upload.py - 文件上传</a></li>
    </ol>
    <h2>运行说明 📖</h2>
    <p>每个示例运行在不同的端口上，请分别运行对应的文件：</p>
    <pre>
python 01_hello.py      # 端口 5000
python 02_routes.py     # 端口 5001
python 03_templates.py  # 端口 5002 (需要 templates 文件夹)
python 04_request_response.py  # 端口 5003
python 05_file_upload.py       # 端口 5004
    </pre>
    <h2>学习要点 💡</h2>
    <ul>
        <li><strong>01_hello.py</strong> - Flask 应用基本结构、路由装饰器</li>
        <li><strong>02_routes.py</strong> - 动态URL、类型转换器、HTTP方法</li>
        <li><strong>03_templates.py</strong> - Jinja2模板引擎、变量、循环、条件</li>
        <li><strong>04_request_response.py</strong> - request对象、Cookie、Session、JSON</li>
        <li><strong>05_file_upload.py</strong> - 文件上传处理、安全文件名</li>
    </ul>
    """


if __name__ == "__main__":
    app.run(debug=True, port=5555)
