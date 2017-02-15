# -*- coding: utf-8 -*-


from flask import request, abort
from flask_restful import Resource, reqparse, marshal

from config import adowner_fields
from data import adowners


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
        return {"success": True,
                "message": "",
                "data": [marshal(adowner, adowner_fields) for adowner in
                         adowners]}

    def post(self):
        if not request.is_json:
            abort(401)
        else:
            root_args = self.root_reqparser.parse_args()
            # 需要先获得 root_args, 作为 adowner_reqparser 的参数
            adowner_args = self.adowner_reqparser.parse_args(root_args)
            oem_id = adowner_args["id"]
            bdx_id = adowners[-1]["bdx_id"] + 1
            names = [adowner["name"] for adowner in adowners]
            if adowner_args["name"] in names:
                abort(401, "AdOwner's name is already in use.")
            adowner = {
                "oem_id": oem_id,
                "bdx_id": bdx_id,
                "name": adowner_args["name"],
                "area": adowner_args["area"],
                "category": adowner_args["category"],
                "brand": adowner_args["brand"],
                "turn": adowner_args["turn"],
                "url": adowner_args["url"],
                "lic": adowner_args["lic"],
                "org": adowner_args["org"],
                "tax": adowner_args["tax"],
                "reg": adowner_args["reg"],
                "icp": adowner_args["icp"],
                "card": adowner_args["card"],
                "adx": root_args["adx"],
                "adx_id": root_args["adx_id"],
                "bdx_materials": [
                    {"type_id": material["TypeId"], "name": material["Name"],
                     "path": material["Path"]} for material in
                    adowner_args["bdx_materials"]]
            }
            adowners.append(adowner)
            return {
                "success": True,
                "message": "",
                "data": {"qualification": {oem_id: bdx_id}}
            }


class AdvertiserAPI(Resource):
    def __init__(self):
        set_reqparser(self)
        super(AdvertiserAPI, self).__init__()

    def get(self, id):
        adowner = filter(lambda t: t["oem_id"] == id, adowners)
        if len(adowner) == 0:
            abort(404)
        return {"success": True, "message": "",
                "data": adowner}

    def put(self, id):
        if not request.is_json:
            abort(401)
        else:
            adowner_orig = filter(lambda t: t["oem_id"] == id, adowners)
            if len(adowner_orig) == 0:
                abort(404)
            adowner_orig = adowner_orig[0]
            root_args = self.root_reqparser.parse_args()
            adowner_args = self.adowner_reqparser.parse_args(root_args)
            if adowner_orig["name"] != adowner_args["name"]:
                abort(401, "Update adowner's name is forbidden.")
            adowner = {
                "oem_id": adowner_args["id"],
                "bdx_id": adowner_orig["bdx_id"],
                "name": adowner_args["name"],
                "area": adowner_args["area"],
                "category": adowner_args["category"],
                "brand": adowner_args["brand"],
                "turn": adowner_args["turn"],
                "url": adowner_args["url"],
                "lic": adowner_args["lic"],
                "org": adowner_args["org"],
                "tax": adowner_args["tax"],
                "reg": adowner_args["reg"],
                "icp": adowner_args["icp"],
                "card": adowner_args["card"],
                "adx": root_args["adx"],
                "adx_id": root_args["adx_id"],
                "bdx_materials": [
                    {"type_id": material["TypeId"], "name": material["Name"],
                     "path": material["Path"]} for material in
                    adowner_args["bdx_materials"]]
            }
            # 更新操作由删除和新增两个操作组成, 必须在一起
            adowners.remove(adowner_orig)
            adowners.append(adowner)
            return {
                "success": True,
                "message": "",
                "data": {
                    "qualification": {adowner["oem_id"]: adowner["bdx_id"]}
                }
            }

    def delete(self, id):
        adowner = [adowner for adowner in adowners if adowner["oem_id"] == id]
        if len(adowner) == 0:
            abort(404, "AdOwner doesn't exist.")
        adowners.remove(adowner[0])
        return {"success": True, "message": ""}
