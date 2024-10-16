from flask import Flask, request, make_response, jsonify
import os
import json
import subprocess

app = Flask(__name__)


@app.route("/len", methods=['GET'])
def get_user_count():
    DIR = '/root/WG_app/static'
    user_count = sum([len(files) for r, d, files in os.walk(DIR)])
    return {"user_count": user_count}


@app.route("/createWG", methods=['POST'])
def create_user():
    js = request.get_json()
    key = js.get('chat_id')
    if not key:
        return make_response(
            jsonify({"success": False, "error": "Not Authorized"}), 401)

    config_path = f'/app/static/wg0-client-{str(key)}.conf'

    if not os.path.isfile(config_path):
        subprocess.call(
            f'/bin/bash /app/sh/addusertovpn.sh {str(key)}',
            shell=True
        )

    if os.path.isfile(config_path):
        with open(config_path, "r") as file:
            config_content = file.read()
        return make_response(config_content, 200,
                             {'Content-Type': 'text/plain'})
    else:
        return make_response(
            jsonify(
                {"success": False, "error": "Configuration file not found"}
            ),
            404
        )


@app.route("/deleteWG", methods=['DELETE'])
def delete_user():
    js = json.loads(request.data)
    key = js.get('chat_id')
    if not key:
        return make_response({"success": False, "error": "Not Authorized"},
                             401)

    subprocess.call(f'/sh/deleteuserfromvpn.sh {str(key)}',
                    shell=True)
    config_path = f'/root/WG_app/static/wg0-client-{str(key)}.conf'
    if os.path.isfile(config_path):
        os.remove(config_path)

    return {"success": True}


@app.route("/getConfig", methods=['GET'])
def get_config():
    js = json.loads(request.data)
    key = js.get('chat_id')
    if not key:
        return make_response({"success": False, "error": "Not Authorized"},
                             401)

    config_path = f'/root/WG_app/static/wg0-client-{str(key)}.conf'
    if os.path.isfile(config_path):
        with open(config_path, 'r') as file:
            config_data = file.read()
        return {"config": config_data}
    else:
        return make_response(
            {"success": False, "error": "Config not found"}, 404
        )

if __name__ == '__main__':
    app.run("0.0.0.0", port=8080)