from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello, Flask! 你好，亲爱的主人！🌸"


@app.route("/greet/<name>")
def greet(name):
    return f"你好，{name}！欢迎学习 Flask～ ✨"


if __name__ == "__main__":
    app.run(debug=True, port=5000)
