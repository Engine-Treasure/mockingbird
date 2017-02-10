# -*-coding: utf-8 -*-

from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask import Flask, redirect, make_response, render_template

app = Flask(__name__)  # Flask 用这个参数决定程序的根目录
app.debug = True

bootstrap = Bootstrap(app)
manager = Manager(app)


@app.route("/")
def index():
    return render_template("index.html")


# <name> 为 URL 的动态部分，作为参数传入视图函数
@app.route("/user/<name>")
def user(name):
    return render_template("user.html", name=name)


@app.route("/redirect1")
def redirect1():
    return redirect("http://kissg.me")


@app.route("/redirect2")
def redirect2():
    response = make_response("", 302, {"Location": "http://kissg.me"})
    return response


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    manager.run()
