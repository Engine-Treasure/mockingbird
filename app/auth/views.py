# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-03-06"

import hashlib

from flask import render_template, redirect, request, url_for, flash, \
    current_app
from flask_login import login_required, login_user, logout_user, current_user

from app import db
from . import auth
from .forms import LoginForm, RegistrationForm, UpdatepasswordForm, \
    ResetpasswordForm_email, ResetpasswordForm_password, UpdateemailForm
from ..email import send_email
from ..models import User

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@auth.before_app_request
def before_request():
    """
    未验证用户登录, 重定向. 或者称为拦截请求
    1) 用户以登录
    2) 用户未验证
    3) 请求的断点不在蓝本中
    """
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint[:5] != "auth.":
            return redirect(url_for("auth.unconfirmed"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        # 提交数据库后, 才能赋予新用户 id 值, 从而确认令牌需要用到的 id, 不能延迟提交
        token = user.generate_confirmation_token()
        send_email(user.email, "Confirm Your Account", "mail/confirm",
                   user=user, token=token)
        flash("A confirmation email has been sent to you by email.")
        return redirect(url_for("auth.unconfirmed"))
    return render_template("auth/register.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get("next") or url_for("main.index"))
        flash("Invalid username or password.")
    return render_template("auth/login.html", form=form)


@auth.route("/confirm/<token>")
@login_required  # 该装饰器会包含路由, 只允许登录的用户访问该路由
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    if current_user.confirm(token):
        flash("You have confirmed your account. Thanks!")
    else:
        flash("The confirmation links is invalid or has expird.")
    return redirect(url_for("main.index"))


@auth.route("/unconfirmed")
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for("main.index"))
    return render_template("auth/unconfirmed.html")


@auth.route("/confirm")
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, "Confirm Your Account",
               "mail/confirm", user=current_user, token=token)
    flash("A new confirmation email has been sent to you by email.")
    return redirect(url_for("main.index"))


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("main.index"))


@auth.route("/settings")
@login_required
def settings():
    return render_template("auth/settings.html")


@auth.route("/update_password", methods=["GET", "POST"])
@login_required
def update_password():
    form = UpdatepasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id=current_user.id).first()
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        logout_user()
        flash("Update password succeed. Please login again.")
        return redirect(url_for("auth.login"))
    return render_template("auth/update_password.html", form=form)


@auth.route("/check_account", methods=["GET", "POST"])
def check_account():
    form = ResetpasswordForm_email()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        token = user.generate_confirmation_token()
        send_email(user.email, "Reset Password", "mail/reset_password",
                   user=user, token=token)
        flash("A email has been sent to you by email.")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form=form)


@auth.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    form = ResetpasswordForm_password()
    if form.validate_on_submit():
        user_id = Serializer(current_app.config["SECRET_KEY"]).loads(token).get(
            "confirm")
        user = User.query.filter_by(id=user_id).first()
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        flash("Reset password succeed. You can login with your new password.")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form=form)


@auth.route("/update_email", methods=["GET", "POST"])
@login_required
def update_email():
    form = UpdateemailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id=current_user.id).first()
        token = user.generate_confirmation_token(email=form.email.data)
        send_email(form.email.data, "Reset Email", "mail/update_email",
                   token=token)
        flash("A email has been sent to your new email address, \
            please check it.")
        return redirect(url_for("auth.login"))
    return render_template("auth/update_email.html", form=form)


@auth.route("/confirm_new_email/<token>", )
def confirm_new_email(token):
    user_info = Serializer(current_app.config["SECRET_KEY"]).loads(token)
    user = User.query.filter_by(id=user_info.get("confirm")).first()
    user.email = user_info.get("email")
    user.avatar_hash = hashlib.md5(user.email.encode('utf-8')).hexdigest()
    db.session.add(user)
    flash("Update email succeed. You can login with your new email.")
    return redirect(url_for("auth.login"))
