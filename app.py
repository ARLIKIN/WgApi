import os

from http import HTTPStatus
from flask import Flask, request, jsonify, make_response

from service.config import STATIC_DIR, DIR_KEY_TEMPLATE, HOST, PORT
from service.service import (
    auth_required,
    error_check_exist_user_id,
    execute_command,
    read_config,
    return_config,
    error_not_found_config
)

app = Flask(__name__)

@app.route("/len", methods=['GET'])
@auth_required
def get_user_count():
    user_count = sum(len(files) for _, _, files in os.walk(STATIC_DIR))
    return jsonify({"success": True, "user_count": user_count})


@app.route("/createWG", methods=['POST'])
@auth_required
def create_user():
    js = request.get_json()
    key = js.get('name_key')
    if not key:
       return error_check_exist_user_id()
    if not os.path.isfile(DIR_KEY_TEMPLATE.format(name=key)):
        if not execute_command(f'wg/add_user.sh {key}', app):
            return make_response(
                jsonify(
                    {"success": False, "error": "Failed to create user"}
                ),
                HTTPStatus.INTERNAL_SERVER_ERROR
            )

    config_content = read_config(key)
    if config_content:
        return return_config(config_content)
    else:
        return error_not_found_config()


@app.route("/deleteWG", methods=['DELETE'])
@auth_required
def delete_user():
    js = request.get_json()
    key = js.get('name_key')
    if not key:
        return error_check_exist_user_id()
    if not execute_command(f'wg/delete_user.sh {key}', app):
        return make_response(
            jsonify(
                {"success": False, "error": "Failed to delete user"}
            ),
            HTTPStatus.INTERNAL_SERVER_ERROR
        )
    return jsonify({"success": True})


@app.route("/getConfig", methods=['GET'])
@auth_required
def get_config():
    js = request.get_json()
    key = js.get('name_key')
    if not key:
       return error_check_exist_user_id()
    config_content = read_config(key)
    if config_content:
        return return_config(config_content)
    else:
        return error_not_found_config()


if __name__ == '__main__':
    host = HOST
    port = PORT
    app.run(host=host, port=port)
