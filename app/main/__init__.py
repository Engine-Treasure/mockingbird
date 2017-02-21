# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-02-21"


from flask import Blueprint


main = Blueprint("main", __name__)


# 放在末尾的原因是： 避免循环导入依赖
from . import views, errors
