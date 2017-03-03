# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-02-21"

from datetime import datetime

from flask import render_template, session, redirect, url_for

from config import Config
from . import main
from .forms import NameForm
from .. import db
from ..models import User
from ..utils import send_email


# 由蓝本提供路由装饰器
@main.route("/", methods=["GET", "POST"])
def index():
    form = NameForm()
    if form.validate_on_submit():  # 数据能被所有验证函数接受
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if Config.MOCKINGBIRD_ADMIN:
                send_email(Config.MOCKINGBIRD_ADMIN, "New User",
                           "mail/new_user", user=user)
        else:
            session["known"] = True
        session['name'] = form.name.data
        form.name.data = ""
        # Flask 会为蓝本中的全部端点加上一个命名空间 (命名空间即蓝本的名字)
        # 于是可以在不同蓝本中使用相同的端点名定义视图函数
        return redirect(url_for("main.index", current_time=datetime.utcnow()))
    return render_template("index.html",
                           # session.get 避免为找到键的异常情况
                           form=form, name=session.get("name"),
                           known=session.get("known", False),
                           current_time=datetime.utcnow())
