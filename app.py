import os
import subprocess

from http import HTTPStatus
from dotenv import load_dotenv
from flask import Flask, request, jsonify, make_response

load_dotenv()

app = Flask(__name__)

DIR_KEY_TEMPLATE = 'wg/static/wg0-client-{name}.conf'
STATIC_DIR = 'wg/static'


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


@app.route("/len", methods=['GET'])
def get_user_count():
    user_count = sum(len(files) for _, _, files in os.walk(STATIC_DIR))
    return jsonify({"success": False, "user_count": user_count})


@app.route("/createWG", methods=['POST'])
def create_user():
    js = request.get_json()
    key = js.get('chat_id')
    if not key:
        return make_response(
            jsonify({"success": False, "error": "Not Authorized"}),
            HTTPStatus.UNAUTHORIZED
        )

    if not os.path.isfile(DIR_KEY_TEMPLATE.format(name=key)):
        if not execute_command(f'wg/addusertovpn.sh {key}'):
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
def delete_user():
    js = request.get_json()
    key = js.get('chat_id')
    if not key:
        return make_response(
            jsonify({"success": False, "error": "Not Authorized"}),
            HTTPStatus.UNAUTHORIZED
        )
    if not execute_command(f'wg/deleteuserfromvpn.sh {key}'):
        return make_response(
            jsonify(
                {"success": False, "error": "Failed to delete user"}
            ),
            HTTPStatus.INTERNAL_SERVER_ERROR
        )
    return jsonify({"success": True})


@app.route("/getConfig", methods=['GET'])
def get_config():
    js = request.get_json()
    key = js.get('chat_id')
    if not key:
        return make_response(
            jsonify({"success": False, "error": "Not Authorized"}),
            HTTPStatus.UNAUTHORIZED
        )
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
