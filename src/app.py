#!/usr/bin/python
# -*-coding: utf-8 -*-

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_script import Manager

from api_1_0 import api_bp

app = Flask(__name__)  # Flask 用这个参数决定程序的根目录
app.register_blueprint(api_bp)  # 注册 API 蓝图，很关键

bootstrap = Bootstrap(app)
moment = Moment(app)
manager = Manager(app)
app.test_client()


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    manager.run()
