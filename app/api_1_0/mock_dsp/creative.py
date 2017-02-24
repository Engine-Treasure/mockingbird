# -*- coding: utf-8 -*-


import os
import pickle
import time

from flask import request, abort
from flask_restful import Resource, reqparse
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import AdOwner, Creative

from urllib import urlretrieve


def set_reqparser(self):
    # Automatic parameter authentication
    # Nested JSON, level 1
    self.root_reqparser = reqparse.RequestParser()
    self.root_reqparser.add_argument("creatives", type=dict, required=True,
                                     location="json")

    # Nested JSON, level 2 - creative
    self.creative_reqparser = reqparse.RequestParser()
    self.creative_reqparser.add_argument("id", type=int, required=True,
                                         help="Creative Id is required.",
                                         location="creatives")
    self.creative_reqparser.add_argument("name", type=str, required=True,
                                         help="Creative name is required.",
                                         location="creatives")
    self.creative_reqparser.add_argument("size", type=str, required=True,
                                         help="Creative size is required.",
                                         location="creatives")
    self.creative_reqparser.add_argument("type", type=str, required=True,
                                         help="Creative type is required.",
                                         location="creatives")
    self.creative_reqparser.add_argument("file_id", type=str,
                                         location="creatives")
    self.creative_reqparser.add_argument("path", type=str,
                                         location="creatives")
    self.creative_reqparser.add_argument("code", type=str,
                                         location="creatives")
    self.creative_reqparser.add_argument("click", type=str,
                                         location="creatives")
    self.creative_reqparser.add_argument("deep_click", type=str,
                                         location="creatives")
    self.creative_reqparser.add_argument("copy_to_bdx", type=str,
                                         location="creatives")
    self.creative_reqparser.add_argument("status", type=str,
                                         location="creatives")


class CreativesAPI(Resource):
    def __init__(self):
        set_reqparser(self)
        super(CreativesAPI, self).__init__()

    def get(self, aid):
        creatives = [creative.extract() for creative in
                     Creative.query.filter_by(adowner_id_oem=aid).all()]
        return {
            "success": True,
            "message": "",
            "data": creatives
        }

    def post(self, aid):
        if not request.is_json:
            abort(401)
        else:
            root_args = self.root_reqparser.parse_args()
            # 需要先获得 root_args, 作为 creaitve_reqparser 的参数
            creative_args = self.creative_reqparser.parse_args(root_args)
            oem_id = creative_args["id"]
            # file_id 不存在, 且 copy_to-bdx 为False
            if creative_args["file_id"] is None and \
                    not creative_args["copy_to_bdx"]:
                abort(401, "There is no creative material.")
            # file_id 不存在, 但 copy_to_bdx 为 True
            # 下载素材
            elif creative_args["file_id"] is None and \
                    creative_args["copy_to_bdx"]:
                file_id = creative_args["path"].split("/")[-1]
                # 本地已存在同名文件, 新建文件时追加时间戳
                if os.path.isfile(os.path.join("upload_folder", file_id)):
                    filename, ext = os.path.splitext(file_id)
                    file_id = filename + "_" + str(int(time.time())) + ext
                try:
                    urlretrieve(creative_args["path"], file_id)
                except Exception:
                    abort(500)
                creative_args["file_id"] = file_id
            # field_id 存在, 使用 filed_id
            else:
                if not os.path.isfile(os.path.join("upload_folder",
                                                   creative_args["file_id"])):
                    abort(400, "There is no such creative material in server.")
                else:
                    creative = Creative(
                        oem_id=oem_id,
                        name=creative_args["name"],
                        size=creative_args["size"],
                        type_=creative_args["type"],
                        file_id=creative_args["file_id"],
                        path=creative_args["path"],
                        code=creative_args["code"],
                        click=creative_args["click"],
                        deep_click=creative_args["deep_click"],
                        copy_to_bdx=creative_args["copy_to_bdx"],
                        status=creative_args["status"],
                        adowner_id_oem=aid
                    )
                    try:
                        db.session.add(creative)
                        db.session.commit()
                    except IntegrityError:
                        db.session.rollback()
                        abort(400, "Creative id or name is already in used.")

                    return {
                        "success": True,
                        "message": "",
                        "data": {"creative": {oem_id: creative.bdx_id}}
                    }


class CreativeAPI(Resource):
    def __init__(self):
        set_reqparser(self)
        super(CreativeAPI, self).__init__()

    def get(self, aid, cid):
        creative = Creative.query.filter_by(oem_id=cid).first()
        return {
            "success": True,
            "message": "",
            "data": creative.extract()
        }

    # 根据 cid 在数据库中查询创意, 创意 oem_id 可更改
    def put(self, aid, cid):
        if not request.is_json:
            abort(401)
        else:
            root_args = self.root_reqparser.parse_args()
            # 需要先获得 root_args, 作为 creaitve_reqparser 的参数
            creative_args = self.creative_reqparser.parse_args(root_args)
            creative = Creative.query.filter_by(oem_id=cid).first()
            if creative is None:
                abort(400, "Creative doesn't exist.")

            # file_id 不存在, 且 copy_to-bdx 为False
            if creative_args["file_id"] is None and \
                    not creative_args["copy_to_bdx"]:
                abort(401, "There is no creative material.")
            # file_id 不存在, 但 copy_to_bdx 为 True
            # 下载素材
            elif creative_args["file_id"] is None and \
                    creative_args["copy_to_bdx"]:
                file_id = creative_args["path"].split("/")[-1]
                # 本地已存在同名文件, 新建文件时追加时间戳
                if os.path.isfile(os.path.join("upload_folder", file_id)):
                    filename, ext = os.path.splitext(file_id)
                    file_id = filename + "_" + str(int(time.time())) + ext
                try:
                    urlretrieve(creative_args["path"], file_id)
                except Exception:
                    abort(500)
                creative_args["file_id"] = file_id
            # field_id 存在, 使用 filed_id
            else:
                if not os.path.isfile(os.path.join("upload_folder",
                                                   creative_args["file_id"])):
                    abort(400, "There is no such creative material in server.")
                else:
                    creative.oem_id = creative_args["id"]  # 允许改变 oem_id
                    creative.name = creative_args["name"]
                    creative.size = creative_args["size"]
                    creative.type = creative_args["type"]
                    creative.file_id = creative_args["file_id"]
                    creative.path = creative_args["path"]
                    creative.code = creative_args["code"]
                    creative.click = creative_args["click"]
                    creative.deep_click = creative_args["deep_click"]
                    creative.copy_to_bdx = creative_args["copy_to_bdx"]
                    creative.status = creative_args["status"]
                    creative.adowner_id_oem = aid
                    try:
                        db.session.commit()
                    except IntegrityError:
                        db.session.rollback()
                        abort(400, "Creative id or name is alreay in used")

                    return {
                        "success": True,
                        "message": "",
                        "data": {
                            "creative": {creative_args["id"]: creative.bdx_id}}
                    }

    def delete(self, aid, cid):
        creative = Creative.query.filter_by(oem_id=cid).first()
        if creative is None:
            abort(404, "Creative doesn't exist.")
        try:
            db.session.delete(creative)
            db.session.commit()
        except Exception:
            db.session.rollback()
            abort(500)
        return {"success": True, "message": ""}
