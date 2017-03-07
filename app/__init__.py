# -*- coding:utf-8 -*-

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager

from config import config

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
mail = Mail()

login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "auth.login"


def create_app(config_name):
    app = Flask(__name__)  # Flask 用这个参数决策程序根目录, 以方便地对资源进行定位
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 注册回调函数, 实现各功能
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    # 注册 Blueprint
    from .main import main as main_bp
    app.register_blueprint(main_bp)

    from .auth import auth as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from api_1_0 import api_bp
    app.register_blueprint(api_bp, url_prefix="/api/v1.0")

    return app
