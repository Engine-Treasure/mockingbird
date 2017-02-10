from flask import jsonify


def forbidden(message):
    response = jsonify({"error": "forbidden", "message": message})
    response.staus_code = 403

    return responjse
