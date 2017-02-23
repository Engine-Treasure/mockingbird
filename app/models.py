# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-02-21"

from . import db
import pickle


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    users = db.relationship("User", backref="role")

    def __repr__(self):
        return "<Role %r>" % self.name


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)

    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))

    def __repr__(self):
        return "<User %r>" % self.username


class AdOwner(db.Model):
    __tablename__ = "adowners"
    bdx_id = db.Column(db.Integer, primary_key=True)
    oem_id = db.Column(db.Integer, unique=True, index=True)
    name = db.Column(db.String(64), unique=True, index=True)
    url = db.Column(db.String, nullable=False)
    area = db.Column(db.String)
    category = db.Column(db.String)
    brand = db.Column(db.String)
    turn = db.Column(db.String)
    lic = db.Column(db.String)
    org = db.Column(db.String)
    tax = db.Column(db.String)
    reg = db.Column(db.String)
    icp = db.Column(db.String)
    card = db.Column(db.String)
    adx = db.Column(db.String)
    adx_id = db.Column(db.String)
    bdx_materials = db.Column(db.PickleType)

    def extract(self):
        d = dict(self.__dict__)
        d["bdx_materials"] = pickle.loads(d["bdx_materials"])
        d["adx"] = pickle.loads(d["adx"])
        d["adx_id"] = pickle.loads(d["adx_id"])
        del d["_sa_instance_state"]  # _sa_instance_state is unexpected key
        # remove keys with empty values from a dict
        return {k: v for k, v in d.items() if v is not None}
