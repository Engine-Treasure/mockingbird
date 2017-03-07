# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-03-06"

import pickle

from app import db


class AdOwner(db.Model):
    __tablename__ = "adowners"

    bdx_id = db.Column(db.Integer, primary_key=True)
    oem_id = db.Column(db.Integer, unique=True, index=True)
    name = db.Column(db.String(64), unique=True, index=True)
    url = db.Column(db.String(128), nullable=False)
    area = db.Column(db.String(128))
    category = db.Column(db.String(64))
    brand = db.Column(db.String(64))
    turn = db.Column(db.String(128))
    lic = db.Column(db.String(128))
    org = db.Column(db.String(128))
    tax = db.Column(db.String(128))
    reg = db.Column(db.String(128))
    icp = db.Column(db.String(128))
    card = db.Column(db.String(128))
    adx = db.Column(db.String)
    adx_id = db.Column(db.String)
    bdx_materials = db.Column(db.String)

    creatives = db.relationship("Creative", backref="adowner", lazy="dynamic")

    def __init__(self, oem_id, name, url, area, category, brand, turn, lic, org,
                 tax, reg, icp, card, adx, adx_id, bdx_materials):
        self.oem_id = oem_id
        self.name = name
        self.url = url
        self.area = area
        self.category = category
        self.brand = brand
        self.turn = turn
        self.lic = lic
        self.org = org
        self.tax = tax
        self.reg = reg
        self.icp = icp
        self.card = card
        self.adx = adx
        self.adx_id = adx_id
        self.bdx_materials = bdx_materials

    def __repr__(self):
        return '<AdOwner %r>' % self.oem_id

    def extract(self):
        d = dict(self.__dict__)
        d["bdx_materials"] = pickle.loads(d["bdx_materials"])
        d["adx"] = pickle.loads(d["adx"])
        d["adx_id"] = pickle.loads(d["adx_id"])
        del d["_sa_instance_state"]  # _sa_instance_state is unexpected key
        # remove keys with empty values from a dict
        return {k: v for k, v in d.items() if v is not None}


class Creative(db.Model):
    __tablename__ = "creatives"

    bdx_id = db.Column(db.Integer, primary_key=True)
    oem_id = db.Column(db.Integer, unique=True, index=True)
    name = db.Column(db.String(64), unique=True, index=True)
    size = db.Column(db.String(16))
    type = db.Column(db.String(16))
    file_id = db.Column(db.String(64))
    path = db.Column(db.String(128))
    code = db.Column(db.String(128))
    click = db.Column(db.String(128))
    deep_click = db.Column(db.String(128))
    copy_to_bdx = db.Column(db.Boolean)
    status = db.Column(db.Integer)

    adowner_bdx_id = db.Column(db.Integer, db.ForeignKey("adowners.bdx_id"))

    def __init__(self, oem_id, name, size, type_, file_id, path, code, click,
                 deep_click, copy_to_bdx, status, adowner_bdx_id):
        self.oem_id = oem_id
        self.name = name
        self.size = size
        self.type = type_
        self.file_id = file_id
        self.path = path
        self.code = code
        self.click = click
        self.deep_click = deep_click
        self.copy_to_bdx = copy_to_bdx
        self.status = status
        self.adowner_bdx_id = adowner_bdx_id

    def __repr__(self):
        return '<Creative %r>' % self.oem_id

    def extract(self):
        d = dict(self.__dict__)
        del d["_sa_instance_state"]  # _sa_instance_state is unexpected key
        d["adowner_id"] = d.pop("adowner_id_oem")
        # remove keys with empty values from a dict
        return {k: v for k, v in d.items() if v is not None}
