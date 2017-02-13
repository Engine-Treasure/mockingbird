from flask import Blueprint
from flask_restful import Api

from . import mock_dsp, mock_todo

api_bp = Blueprint("api", __name__)

api_todo = Api(api_bp)

api_todo.add_resource(mock_todo.TaskListAPI, "/todo/api/v1.0/tasks",
                      endpoint="tasks")
api_todo.add_resource(mock_todo.TaskAPI, "/todo/api/v1.0/task/<int:id>",
                      endpoint="task")
