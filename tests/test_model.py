# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-03-06"


import unittest

from app.models import User


class UserModelTestCase(unittest.TestCase):
    def test_password_setter(self):
        u = User(password="Echo")
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password="Echo")
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password="Echo")
        self.assertTrue(u.verify_password("Echo"))
        self.assertFalse(u.verify_password("Engine"))

    def test_password_salts_are_random(self):
        u = User(password="Echo")
        u2 = User(password="Echo")
        self.assertTrue(u.password_hash != u2.password_hash)
        self.assertFalse(u.verify_password("Engine"))
