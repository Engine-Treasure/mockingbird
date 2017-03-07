# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-03-06"

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo

from ..models import User


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Keep me logged in.")
    submit = SubmitField("Log in")

    # validate_ 开头的方法, 与常规的验证函数一起调用
    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError("Account doesn't exist.")


class RegistrationForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField("Username", validators=[
        DataRequired(), Length(1, 64), Regexp("^[A-Za-z][A-Za-z0-9_.]*$",
                                              0, "Usernames must have only"
                                                 "letters, numbers, dots or "
                                                 "underscores")
    ])
    password = PasswordField("Password", validators=[DataRequired(),
                                                     EqualTo("password2",
                                                             message=
                                                             "Passwords must match.")])
    password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Register")

    # validate_ 开头的方法, 与常规的验证函数一起调用
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email already registered.")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Username already in use.")


class UpdatepasswordForm(FlaskForm):
    old_password = PasswordField("Old Password", validators=[DataRequired()])
    password = PasswordField("New Password", validators=[DataRequired(),
                                                         EqualTo("password2",
                                                                 message="Passwords must match.")])
    password2 = PasswordField("Confirm New password",
                              validators=[DataRequired()])
    submit = SubmitField("Update password")


class ResetpasswordForm_email(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(1, 64),
                                             Email()])

    # validate_ 开头的方法, 与常规的验证函数一起调用
    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError("Account doesn't exist.")

    submit = SubmitField("Confirm")


class ResetpasswordForm_password(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired(),
                                                         EqualTo("password2",
                                                                 message="Passwords must match.")])
    password2 = PasswordField("Confirm New password",
                              validators=[DataRequired()])
    submit = SubmitField("Reset password")
