import os
import subprocess
from functools import wraps

from http import HTTPStatus
from flask import request, jsonify, make_response

from service.config import DIR_KEY_TEMPLATE, ADMIN_USERNAME, ADMIN_PASSWORD


def execute_command(command, app):
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

def error_not_found_config():
    return make_response(
        jsonify({"success": False, "error": "Config not found"}),
        HTTPStatus.NOT_FOUND
    )

def return_config(config_content):
    return make_response(
        jsonify({"success": True, "config": config_content}),
        HTTPStatus.OK
    )