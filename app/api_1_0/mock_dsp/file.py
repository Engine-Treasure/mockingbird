# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-02-23"

import os
from io import BytesIO

from PIL import Image
from flask import request, abort
from flask_restful import Resource, reqparse

from app.utils import gen_random_str


def set_reqparser(self):
    self.root_reqparser = reqparse.RequestParser()
    self.root_reqparser.add_argument("files", type=str, required=True,
                                     location="form")

    self.file_reqparser = reqparse.RequestParser()
    self.file_reqparser.add_argument("title", type=str, required=True,
                                     location="form")
    self.file_reqparser.add_argument("content", type=str, required=True,
                                     location="files")


class FilesAPI(Resource):
    def __init__(self):
        # set_reqparser(self)
        super(FilesAPI, self).__init__()

    def post(self):
        with Image.open(BytesIO(request.stream.read())) as img:
            type_ = img.format.lower()
            file_id = gen_random_str(6, 10) + "." + type_
            width, height = img.size
            try:
                img.save(os.path.join("upload_folder", file_id))
            except Exception:
                abort(500)
            size = os.stat(os.path.join("upload_folder", file_id)).st_size

            return {"success": True, "message": "",
                    "data": {"id": file_id,
                             "type": type_,
                             "size": size,
                             "width": width,
                             "height": height}}
