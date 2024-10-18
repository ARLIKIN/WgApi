import os
import json
import subprocess

from flask import Flask, request, make_response, jsonify

app = Flask(__name__)

DIR_KEY = 'wg/static/wg0-client-{name}.conf'


@app.route("/len", methods=['GET'])
def get_user_count():
    dir = 'wg/static'
    user_count = sum([len(files) for r, d, files in os.walk(dir)])
    return {"user_count": user_count}


@app.route("/createWG", methods=['POST'])
def create_user():
    js = request.get_json()
    key = js.get('chat_id')
    if not key:
        return make_response(
            jsonify({"success": False, "error": "Not Authorized"}), 401)

    if not os.path.isfile(DIR_KEY.format(name=str(key))):
        subprocess.call(f'wg/addusertovpn.sh {str(key)}', shell=True)

    if os.path.isfile(DIR_KEY.format(name=str(key))):
        with open(DIR_KEY.format(name=str(key)), "r") as file:
            config_content = file.read()
            result = {'config': config_content}
        return make_response(result, 200,
                             {'Content-Type': 'json'})
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

    subprocess.call(f'wg/deleteuserfromvpn.sh {str(key)}', shell=True)
    return {"success": True}


@app.route("/getConfig", methods=['GET'])
def get_config():
    js = json.loads(request.data)
    key = js.get('chat_id')
    if not key:
        return make_response({"success": False, "error": "Not Authorized"},
                             401)
    if os.path.isfile(DIR_KEY.format(name=str(key))):
        with open(DIR_KEY.format(name=str(key)), 'r') as file:
            config_data = file.read()
        return make_response(
            {"config": config_data},
            200,
            {'Content-Type': 'json'}
        )
    else:
        return make_response(
            {"success": False, "error": "Config not found"}, 404
        )

if __name__ == '__main__':
    app.run("0.0.0.0", port=8080)