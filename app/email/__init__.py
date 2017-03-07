# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-03-06"

from threading import Thread

from flask import render_template, current_app
from flask_mail import Message

from app import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    # Important!!!!
    app = current_app._get_current_object()
    msg = Message(recipients=[to],
                  subject=current_app.config[
                              "MOCKINGBIRD_MAIL_SUBJECT_PREFIX"] + subject,
                  sender=current_app.config["MOCKINGBIRD_MAIL_SENDER"])
    msg.body = render_template(template + ".txt", **kwargs)

    thr = Thread(target=send_async_email, args=(app, msg))
    thr.start()  # 不启动线程, 怎么发邮件哦, 是不是傻
    return thr
