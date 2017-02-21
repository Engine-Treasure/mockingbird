from __future__ import absolute_import
import json
import unittest

from app import app


class TestTodoList(unittest.TestCase):
    def setUp(self):
        app.debug = True
        self.app = app.app.test_client()
        self.url = "/todo/api/v1.0/tasks"

    def test_get(self):
        response = self.app.get(self.url,
                                headers={"Accept": "application/json"})
        data = json.loads(response.data.decode("utf-8"))
        print("TodoList-GET")
        self.assertEqual(len(data["tasks"]), int(data["tasks"][-1]["uri"][-1]))

    def test_post(self):
        response = self.app.post(self.url,
                                 headers={"Accept": "application/json",
                                          "Content-Type": "application/json"},
                                 data=json.dumps(
                                     {"title": "Love Echo forever~"}))
        data = json.loads(response.data.decode("utf-8"))
        print("TodoList-POST")
        self.assertEqual(data["task"]["uri"], "/todo/api/v1.0/task/3")
        self.assertEqual(data["task"]["title"], "Love Echo forever~")
        self.assertEqual(data["task"]["description"], "")
        self.assertEqual(data["task"]["done"], False)


class TestTodo(unittest.TestCase):
    def setUp(self):
        app.debug = True
        self.app = app.app.test_client()

    def test_get(self):
        response = self.app.get("/todo/api/v1.0/task/1",
                                headers={"Accept": "application/json"})
        data = json.loads(response.data.decode("utf-8"))
        print("Todo-GET")
        self.assertEqual(data["task"]["uri"], "/todo/api/v1.0/task/1")
        self.assertEqual(data["task"]["title"], "Buy groceries")
        self.assertEqual(data["task"]["description"],
                         "Milk, Cheese, Pizza, Fruit, Tylenol")
        self.assertEqual(data["task"]["done"], False)

    def test_put(self):
        response = self.app.put("/todo/api/v1.0/task/1",
                                headers={"Accept": "application/json",
                                         "Content-Type": "application/json"},
                                data=json.dumps(
                                    {
                                        "description": "I can never love you to much~"}))
        data = json.loads(response.data.decode("utf-8"))
        print("Todo-POST")
        self.assertEqual(data["task"]["uri"], "/todo/api/v1.0/task/1")
        self.assertEqual(data["task"]["title"], "Buy groceries")
        self.assertEqual(data["task"]["description"],
                         "I can never love you to much~")
        self.assertEqual(data["task"]["done"], False)

    def test_delete(self):
        print("Todo-DELETE")
        origin_response = self.app.get("/todo/api/v1.0/tasks",
                                       headers={"Accept": "application/json"})
        origin_length = len(
            json.loads(origin_response.data.decode("utf-8"))["tasks"])
        response = self.app.delete("/todo/api/v1.0/task/1",
                                   headers={"Accept": "application/json"})
        later_response = self.app.get("/todo/api/v1.0/tasks",
                                      headers={"Accept": "application/json"})
        later_length = len(
            json.loads(later_response.data.decode("utf-8"))["tasks"])
        data = json.loads(response.data.decode("utf-8"))
        self.assertEqual(data["result"], True)
        self.assertEqual(origin_length - 1, later_length)


'''
def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestTodoList.test_get())
    suite.addTest(TestTodoList.test_post())
'''

if __name__ == '__main__':
    unittest.main()
