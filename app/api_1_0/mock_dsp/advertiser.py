# -*- coding: utf-8 -*-


import pickle

from flask import request, abort
from flask_restful import Resource, reqparse
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import AdOwner


def set_reqparser(self):
    # Automatic parameter authentication
    # Nested JSON, level 1
    self.root_reqparser = reqparse.RequestParser()
    self.root_reqparser.add_argument("adOwner", type=dict, required=True,
                                     location="json")
    self.root_reqparser.add_argument("adx", type=list,
                                     location="json")
    self.root_reqparser.add_argument("adx_id", type=list,
                                     location="json")

    # Nested JSON, level 2 - adOwner
    self.adowner_reqparser = reqparse.RequestParser()
    self.adowner_reqparser.add_argument("id", type=int, required=True,
                                        help="AdOwner Id is required.",
                                        location="adOwner")
    self.adowner_reqparser.add_argument("name", type=str,
                                        location="adOwner")
    self.adowner_reqparser.add_argument("area", type=str,
                                        location="adOwner")
    self.adowner_reqparser.add_argument("category", type=str,
                                        location="adOwner")
    self.adowner_reqparser.add_argument("brand", type=str,
                                        location="adOwner")
    self.adowner_reqparser.add_argument("turn", type=str,
                                        location="adOwner")
    self.adowner_reqparser.add_argument("url", type=str, location="adOwner")
    self.adowner_reqparser.add_argument("lic", type=str, location="adOwner")
    self.adowner_reqparser.add_argument("org", type=str, location="adOwner")
    self.adowner_reqparser.add_argument("tax", type=str, location="adOwner")
    self.adowner_reqparser.add_argument("reg", type=str, location="adOwner")
    self.adowner_reqparser.add_argument("icp", type=str, location="adOwner")
    self.adowner_reqparser.add_argument("card", type=str,
                                        location="adOwner")
    self.adowner_reqparser.add_argument("bdx_materials", type=list,
                                        location="adOwner")


class AdvertisersAPI(Resource):
    def __init__(self):
        set_reqparser(self)
        super(AdvertisersAPI, self).__init__()

    def get(self):
        adowners = [adowner.extract() for adowner in AdOwner.query.all()]
        return {
            "success": True,
            "message": "",
            "data": adowners
        }

    def post(self):
        if not request.is_json:
            abort(401)
        else:
            root_args = self.root_reqparser.parse_args()
            # 需要先获得 root_args, 作为 adowner_reqparser 的参数
            adowner_args = self.adowner_reqparser.parse_args(root_args)

            if AdOwner.query.filter_by(name=adowner_args["name"]).first() \
                    is not None:
                abort(401, "AdOwner's name is already in use.")
            else:
                oem_id = adowner_args["id"]
                bdx_materials = [dict(
                    type_id=material["TypeId"],
                    name=material["Name"],
                    path=material["Path"]
                ) for material in adowner_args["bdx_materials"]]
                adowner = AdOwner(
                    oem_id=oem_id,
                    name=adowner_args["name"],
                    area=adowner_args["area"],
                    category=adowner_args["category"],
                    brand=adowner_args["brand"],
                    turn=adowner_args["turn"],
                    url=adowner_args["url"],
                    lic=adowner_args["lic"],
                    org=adowner_args["org"],
                    tax=adowner_args["tax"],
                    reg=adowner_args["reg"],
                    icp=adowner_args["icp"],
                    card=adowner_args["card"],
                    adx=pickle.dumps(root_args["adx"]),
                    adx_id=pickle.dumps(root_args["adx_id"]),
                    bdx_materials=pickle.dumps(bdx_materials)
                )
                try:
                    db.session.add(adowner)
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    abort(400, "Id is already in used.")

                return {
                    "success": True,
                    "message": "",
                    "data": {"qualification": {oem_id: adowner.bdx_id}}
                }


class AdvertiserAPI(Resource):
    def __init__(self):
        set_reqparser(self)
        super(AdvertiserAPI, self).__init__()

    def get(self, oem_id):
        adowner = AdOwner.query.filter_by(oem_id=oem_id).first()
        if adowner is None:
            abort(404, "AdOwner doesn't exist.")
        return {"success": True, "message": "",
                "data": adowner.extract()}

    def put(self, oem_id):
        if not request.is_json:
            abort(401)
        else:
            root_args = self.root_reqparser.parse_args()
            # 需要先获得 root_args, 作为 adowner_reqparser 的参数
            adowner_args = self.adowner_reqparser.parse_args(root_args)
            oem_id = adowner_args["oem_id"]
            adowner = AdOwner.query.filter_by(oem_id=oem_id).first()
            if adowner is None:
                abort(400, "AdOwner doesn't exist.")
            elif adowner_args["name"] != adowner.name:
                abort(400, "AdOwner name can't be updated.")
            else:
                bdx_materials = [dict(
                    type_id=material["TypeId"],
                    name=material["Name"],
                    path=material["Path"]
                ) for material in adowner_args["bdx_materials"]]
                adowner.oem_id = oem_id
                adowner.area = adowner_args["area"]
                adowner.category = adowner_args["category"]
                adowner.turn = adowner_args["turn"]
                adowner.url = adowner_args["url"]
                adowner.lic = adowner_args["lic"]
                adowner.org = adowner_args["org"]
                adowner.tax = adowner_args["tax"]
                adowner.reg = adowner_args["reg"]
                adowner.icp = adowner_args["icp"]
                adowner.card = adowner_args["card"]
                adowner.adx = pickle.dumps(root_args["adx"])
                adowner.adx_id = pickle.dumps(root_args["adx_id"])
                adowner.bdx_materials = pickle.dumps(bdx_materials)
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                abort(500)

            return {
                "success": True,
                "message": "",
                "data": {"qualification": {oem_id: adowner.bdx_id}}
            }

    def delete(self, oem_id):
        adowner = AdOwner.query.filter_by(oem_id=oem_id).first()
        if adowner is None:
            abort(404, "AdOwner doesn't exist.")
        try:
            db.session.delete(adowner)
            db.session.commit()
        except Exception:
            db.session.rollback()
            abort(500)
        return {"success": True, "message": ""}
