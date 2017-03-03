# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-02-23"

import random
import string
from threading import Thread

from flask import render_template
from flask_mail import Message

from app import mail
from config import Config


def gen_random_str(mode=1, length=8):
    s = {
        1: string.letters,
        2: string.digits,
        3: string.letters + string.digits,
        4: string.punctuation,
        5: string.letters + string.punctuation,
        6: string.letters + string.digits + string.punctuation,
    }.get(mode, string.letters)
    return "".join(
        random.SystemRandom().choice(s) for _ in range(length))


def send_async_email(app, msg):
    with app.context():  # Flask-Mail 的 send 函数使用 current_app, 需激活 context
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(recipients=[to],
                  subject=Config.MOCKINGBIRD_MAIL_SUBJECT_PREFIX + subject,
                  sender=Config.MOCKINGBIRD_MAIL_SENDER)
    msg.body = render_template(template + ".txt", **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    return thr


if __name__ == '__main__':
    print(gen_random_str())
