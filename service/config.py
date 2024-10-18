import os

from dotenv import load_dotenv
load_dotenv()



DIR_KEY_TEMPLATE = 'wg/static/wg0-client-{name}.conf'
STATIC_DIR = 'wg/static'
HOST = os.getenv('FLASK_HOST', '0.0.0.0')
PORT = int(os.getenv('FLASK_PORT', 8080))
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')