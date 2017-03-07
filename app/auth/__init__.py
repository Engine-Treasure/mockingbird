# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-03-06"


from flask import Blueprint


auth = Blueprint("auth", __name__)


from  . import views
