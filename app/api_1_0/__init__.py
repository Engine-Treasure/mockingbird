from hashlib import md5

from flask import Blueprint, request, abort
from flask_restful import Api

from . import mock_dsp, mock_todo

api_bp = Blueprint("api", __name__)

api = Api(api_bp)


@api_bp.before_request
def before_request():
    uid = request.args.get("uid", type=int)
    ts = request.args.get("ts")
    token = request.args.get("token")
    if uid != 9:
        abort(403)
    elif token != md5("seKUMdXuytClsQWYG1tcQa1x" + ts).hexdigest():
        print md5("seKUMdXuytClsQWYG1tcQa1x" + ts).hexdigest()
        print token
        abort(401)


api.add_resource(mock_todo.TaskListAPI, "/todo/tasks",
                 endpoint="tasks")
api.add_resource(mock_todo.TaskAPI, "/todo/task/<int:id>",
                 endpoint="task")

api.add_resource(mock_dsp.AdvertisersAPI, "/dsp/advertisers",
                 endpoint="advertisers")
api.add_resource(mock_dsp.AdvertiserAPI,
                 "/dsp/advertiser/<int:oem_id>",
                 endpoint="advertiser")

api.add_resource(mock_dsp.CreativesAPI,
                 "/dsp/advertiser/<int:aid>/creatives",
                 endpoint="advertiser_creatives")
api.add_resource(mock_dsp.CreativeAPI,
                 "/dsp/advertiser/<int:aid>/creative/<int:cid>",
                 endpoint="advertiser_creative")

api.add_resource(mock_dsp.FilesAPI, "/dsp/files",
                 endpoint="files")
