# -*- coding: utf-8 -*-


__author__ = "kissg"
__date__ = "2017-02-21"

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # 通用密钥, 可在 Flask 和多个第三方扩展中使用.
    # 本项目中, 用于为 Flask-WTF 生成加密密令
    SECRET_KEY = os.environ.get("SECRET_KEY") \
                 or "Engine, will you love Echo forever?"
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MOCKINGBIRD_MAIL_SUBJECT_PREFIX = "[Mockingbird]"
    MOCKINGBIRD_MAIL_SENDER = "Mockingbird Admin <cwf773810@163.com>"
    MOCKINGBIRD_ADMIN = os.environ.get("MOCKINGBIRD_ADMIN")
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    MOCKINGBIRD_POSTS_PER_PAGE = 10

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = "smtp.163.com"
    MAIL_PORT = 994
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL") or \
        "sqlite:///" + os.path.join(basedir, "data-dev.sqlite")


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL") or \
        "sqlite:///" + os.path.join(basedir, "data-test.sqlite")


class ProductionConfig(Config):
    sqlalchemy_database_uri = os.environ.get("DATABASE_URL") or \
        "sqlite:///" + os.path.join(basedir, "data.sqlite")

config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,

    "default": DevelopmentConfig
}
