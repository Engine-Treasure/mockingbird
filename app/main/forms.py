# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-02-21"

from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required


class NameForm(Form):
    name = StringField("What is your name?", validators=[Required()])
    submit = SubmitField("Submit")
