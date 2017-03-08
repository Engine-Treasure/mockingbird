# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-02-21"

from datetime import datetime

from flask import render_template, session, redirect, url_for, abort, flash
from flask_login import login_required, current_user

from config import Config
from . import main
from .forms import NameForm, EditProfileForm, EditProfileAdminForm
from .. import db
from ..email import send_email
from ..models import User, Role
from app.decorators import admin_required


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


@main.route("/user/<username>")
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template("user.html", user=user)


@main.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash("Your profile has been updated.")
        return redirect(url_for("main.user", username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", form=form)


@main.route("/edit-profile/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash("The profile has been updated.")
        return redirect(url_for("main.user", username=user.usernmae))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template("edit_profile.html", form=form, user=user)
