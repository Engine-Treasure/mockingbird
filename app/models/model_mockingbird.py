# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-02-21"

from datetime import datetime

from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


class Permission(object):
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    # lazy - 禁止自动执行查询
    users = db.relationship("User", backref="role", lazy="dynamic")

    # 不用 __init__ 属性, 可以先实例化对象, 在
    # def __init__(self, name):
    #     self.name = name

    @staticmethod
    def insert_roles():
        roles = {
            "User": (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            "Moderator": (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            "Administrator": (0xff, False)
        }
        for r in roles:
            # 通过角色名查找现有角色, 再更新. 只有当数据库中不存在角色才会创建
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return "<Role %r>" % self.name


# UserMixin - 包含了一些用户方法的默认实现
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))

    confirmed = db.Column(db.Boolean, default=False)

    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            # 这个方法有点新颖的
            # 管理员账户的电子邮件保存在环境变量中, 邮件地址出现在注册请求中时, 赋予权限
            if self.email == current_app.config["MOCKINGBIRD_ADMIN"]:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def __repr__(self):
        return "<User %r>" % self.username

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute.")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 生成令牌, 时效 1 h
    def generate_confirmation_token(self, expiration=3600, **kwargs):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        kwargs.update({"confirm": self.id})
        return s.dumps(kwargs)

    # 验证令牌, 设置 confirmed 属性
    def confirm(self, token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get("confirm") != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def can(self, permissions):
        # 如果角色中包含请求的所有权限位. 返回 True
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        '''每次收到用户请求时, 调用. 在 before_app_request 中调用'''
        self.last_seen = datetime.utcnow()
        db.session.add(self)


class AnonymousUser(AnonymousUserMixin):
    """匿名用户, 用于设置用户未登录时的 current_user.
    程序不用检查用户是否登录, 就能自由调用 current_user.can() 等方法
    保证一致性"""

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    # 回调函数, 用于指定的标识符加载用户
    return User.query.get(int(user_id))
