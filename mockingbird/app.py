# -*-coding: utf-8 -*-

from flask.ext.script import Manager
from flask import Flask, redirect, make_response

app = Flask(__name__)  # Flask 用这个参数决定程序的根目录
app.debug = True


manager = Manager(app)


@app.route("/")
def index():
    return "<h1>Welcome to kissg's World!</h1>"


# <name> 为 URL 的动态部分，作为参数传入视图函数
@app.route("/user/<name>")
def user(name):
    # 返回参数被组装成一个元组, 作为响应对象的参数
    # 第一个参数是 body，第二个是 status，第三个是 headers
    response = make_response("<h1>Welcome, %s!</h1>" % name, 404, dict())
    return response


@app.route("/redirect1")
def redirect1():
    return redirect("http://kissg.me")


@app.route("/redirect2")
def redirect2():
    response = make_response("", 302, {"Location": "http://kissg.me"})
    return response


if __name__ == "__main__":
    manager.run()
