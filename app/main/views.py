# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-02-21"

from flask import render_template, redirect, url_for, abort, flash, request, \
    current_app
from flask_login import login_required, current_user

from app.decorators import admin_required
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm
from .. import db
from ..models import User, Role, Post, Permission


# 由蓝本提供路由装饰器
@main.route("/", methods=["GET", "POST"])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(body=form.body.data,
                    # current_user 是一个真正用户对象的轻包装
                    # DB 需要真正的用户对象
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for("main.index"))
    page = request.args.get("page", 1, type=int)  # 从查询字符串获取页数
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config["MOCKINGBIRD_POSTS_PER_PAGE"],
        error_out=False)  # 页面超出范围, 返回一个空列表; True 时, 则返回 404
    posts = pagination.items
    return render_template("index.html", form=form, posts=posts,
                           pagination=pagination)


@main.route("/user/<username>")
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template("user.html", user=user, posts=posts)


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
