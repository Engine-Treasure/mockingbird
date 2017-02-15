#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import abort
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, reqparse, fields, marshal

auth = HTTPBasicAuth()

tasks = [
    {
        "id": 1,
        "title": u"Buy groceries",
        "description": u"Milk, Cheese, Pizza, Fruit, Tylenol",
        "done": False
    },
    {
        "id": 2,
        "title": u"Learn Python",
        "description": u"Ned to find a good Python tutorial on the web",
        "done": False
    },
]

# server as a template for the `marshal` function
task_fields = {
    "title": fields.String,
    "description": fields.String,
    "done": fields.Boolean,
    "uri": fields.Url("api.task")
    # special type that generates URL, 参数是 `endpoint`
}


# Resource 继承自 Flask 的 `MethodView` 类
class TaskListAPI(Resource):
    # decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("title", type=str, required=True,
                                   help="No task title provided",
                                   location="json")
        self.reqparse.add_argument("description", type=str, default="",
                                   location="json")
        super(TaskListAPI, self).__init__()

    def get(self):
        return {"tasks": [marshal(task, task_fields) for task in tasks]}

    def post(self):
        args = self.reqparse.parse_args()
        task = {
            "id": tasks[-1]["id"] + 1,
            "title": args["title"],
            "description": args["description"],
            "done": False
        }
        tasks.append(task)
        return {"task": marshal(task, task_fields)}, 201


class TaskAPI(Resource):
    # decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("title", type=str, location="json")
        self.reqparse.add_argument("description", type=str, location="json")
        self.reqparse.add_argument("done", type=bool, location="json")
        super(TaskAPI, self).__init__()

    def get(self, id):
        task = [task for task in tasks if task["id"] == id]
        if len(task) == 0:
            abort(404)
        return {"task": marshal(task[0], task_fields)}

    def put(self, id):
        task = filter(lambda t: t["id"] == id, tasks)
        if len(task) == 0:
            abort(404)
        task = task[0]
        args = self.reqparse.parse_args()
        for k, v in args.iteritems():
            if v != None:
                task[k] = v
        return {"task": marshal(task, task_fields)}

    def delete(self, id):
        task = [task for task in tasks if task["id"] == id]
        if len(task) == 0:
            abort(404)
        tasks.remove(task[0])
        return {"result": True}
