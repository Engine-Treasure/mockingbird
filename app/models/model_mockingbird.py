# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-02-21"

import hashlib
from datetime import datetime

from flask import current_app, request
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from markdown import markdown
import bleach

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
    posts = db.relationship("Post", backref="author", lazy="dynamic")

    confirmed = db.Column(db.Boolean, default=False)

    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    avatar_hash = db.Column(db.String(32))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            # 这个方法有点新颖的
            # 管理员账户的电子邮件保存在环境变量中, 邮件地址出现在注册请求中时, 赋予权限
            if self.email == current_app.config["MOCKINGBIRD_ADMIN"]:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
            if self.email is not None and self.avatar_hash is None:
                self.avatar_hash = hashlib.md5(
                    self.email.encode("utf-8")).hexdigest()

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

    def gravatar(self, size=100, default="identicon", rating="g"):
        if request.is_secure:
            url = "https://secure.gravatar.com/avatar"
        else:
            url = "http://gravatar.com/avatar"
        hash_ = self.avatar_hash or hashlib.md5(
            self.email.encode("utf-8")).hexdigest()
        return "{url}/{hash}?s={size}&d={default}&r={rating}".format(
            url=url, hash=hash_, size=size, default=default, rating=rating)

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        from faker import Faker

        fake = Faker()
        seed()
        for i in range(count):
            u = User(email=fake.email(),
                     username=fake.name(),
                     password=fake.password(),
                     confirmed=True,
                     name=fake.name(),
                     location=fake.city(),
                     about_me="".join(fake.sentences()),
                     member_since=fake.date_time())
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


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


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    body_html = db.Column(db.Text)

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        from faker import Faker

        fake = Faker()
        seed()
        user_count = User.query.count()
        for i in range(count):
            # offset 跳过指定的偏移量, 与 first() 搭配, 实现随机选择用户
            u = User().query.offset(randint(0, user_count - 1)).first()
            p = Post(body="".join(fake.paragraph()),
                     timestamp=fake.date_time(),
                     author=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ["a", "abbr", "acronym", "b", "blockquote", "code",
                        "em", "i", "li", "ol", "pre", "strong", "ul",
                        "h1", "h2", "h3", "h4", "h5", "h6", "p"]
        # step3 - linkify 将纯文本的 URL 转换成适当的 <a> 链接
        # Markdown 规范没有自为自动生成的链接提供官方支持
        target.body_html = bleach.linkify(
            # step2 - 删除不在白名单中的标签
            bleach.clean(
                # step1 - Convert
                markdown(value, output_format="html"), tags=allowed_tags,
                strip=True))


# 监听 SQLAlchemy 的 set 事件
db.event.listen(Post.body, "set", Post.on_changed_body)
