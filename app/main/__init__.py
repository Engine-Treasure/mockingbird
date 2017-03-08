# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-02-21"

from flask import Blueprint

from ..models import Permission

main = Blueprint("main", __name__)


@main.app_context_processor
def inject_permissions():
    """将 Permission 类加入模板上下文, 带着到处走,
    而不必每次调用 render_template 时多添加一个模板参数"""
    return dict(Permission=Permission)


# 放在末尾的原因是： 避免循环导入依赖
from . import views, errors
