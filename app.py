import os
import subprocess
from functools import wraps

from http import HTTPStatus
from dotenv import load_dotenv
from flask import Flask, request, jsonify, make_response

load_dotenv()

app = Flask(__name__)

DIR_KEY_TEMPLATE = 'wg/static/wg0-client-{name}.conf'
STATIC_DIR = 'wg/static'
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')


def execute_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Error executing command: {command}, {e}")
        return False
    return True


def read_config(key):
    config_path = DIR_KEY_TEMPLATE.format(name=key)
    if os.path.isfile(config_path):
        with open(config_path, 'r') as file:
            return file.read()
    return None


def auth_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        auth = request.authorization
        if (
            not auth or auth.username != ADMIN_USERNAME
            or auth.password != ADMIN_PASSWORD
        ):
            return make_response(
                jsonify({"success": False, "error": "Not Authorized"}),
                HTTPStatus.UNAUTHORIZED
            )
        return f(*args, **kwargs)
    return decorator


def error_check_exist_user_id():
    return make_response(
        jsonify({"success": False, "error": "Not user id"}),
        HTTPStatus.BAD_REQUEST
    )


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
        if not execute_command(f'wg/add_user.sh {key}'):
            return make_response(
                jsonify(
                    {"success": False, "error": "Failed to create user"}
                ),
                HTTPStatus.INTERNAL_SERVER_ERROR
            )

    config_content = read_config(key)
    if config_content:
        return make_response(
            jsonify({"success": True, "config": config_content}),
            HTTPStatus.OK
        )
    else:
        return make_response(
            jsonify(
                {"success": False, "error": "Configuration file not found"}
            ),
            HTTPStatus.NOT_FOUND
        )


@app.route("/deleteWG", methods=['DELETE'])
@auth_required
def delete_user():
    js = request.get_json()
    key = js.get('name_key')
    if not key:
        return error_check_exist_user_id()
    if not execute_command(f'wg/delete_user.sh {key}'):
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
        return make_response(
            jsonify({"config": config_content}),
            HTTPStatus.OK
        )
    else:
        return make_response(
            jsonify({"success": False, "error": "Config not found"}),
            HTTPStatus.NOT_FOUND
        )


if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 8080))
    app.run(host=host, port=port)
