import json
import os
import uuid
from datetime import datetime
from cryptography.fernet import Fernet
from splunk.persistconn.application import PersistentServerConnectionApplication

SPLUNK_HOME = os.environ.get("SPLUNK_HOME", "/opt/splunk")
APP_NAME = "adv_dashboards"
APP_DIR = os.path.join(SPLUNK_HOME, "etc", "apps", APP_NAME)
CONFIG_PATH = os.path.join(APP_DIR, "local", "credential.conf")
KEY_DIR = os.path.join(APP_DIR, "etc", "auth")
DEBUG_FILE = os.path.join(APP_DIR, "var", "log", "debug_input.txt")


def write_debug(data):
    os.makedirs(os.path.dirname(DEBUG_FILE), exist_ok=True)
    with open(DEBUG_FILE, "a") as f:
        f.write("\n--- DEBUG ---\n")
        f.write(json.dumps(data, indent=2))
        f.write("\n")


def get_or_create_key():
    os.makedirs(KEY_DIR, exist_ok=True)

    for fname in os.listdir(KEY_DIR):
        if fname.endswith(".key"):
            with open(os.path.join(KEY_DIR, fname), "rb") as f:
                return fname, f.read()

    key = Fernet.generate_key()
    key_name = f"key_{uuid.uuid4().hex}.key"
    with open(os.path.join(KEY_DIR, key_name), "wb") as f:
        f.write(key)
    return key_name, key


class UpdateCreds(PersistentServerConnectionApplication):
    def __init__(self, _command_line, _command_arg):
        super(PersistentServerConnectionApplication, self).__init__()

    def handle(self, in_string):
        try:
            if isinstance(in_string, bytes):
                in_string = in_string.decode("utf-8")

            req = json.loads(in_string)
            form_data = req.get("form", [])
            data = {key: value for key, value in form_data}

            write_debug({"raw_input": in_string, "parsed_form": data})

            url = data.get("url")
            username = data.get("username")
            password = data.get("password")

            if not all([url, username, password]):
                return {'payload': {'error': 'Missing one or more required fields'}, 'status': 400}

            key_name, key = get_or_create_key()
            fernet = Fernet(key)
            encrypted_password = fernet.encrypt(password.encode()).decode()

            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

            with open(CONFIG_PATH, "w") as f:
                f.write("[settings]\n")
                f.write(f"url = {url}\n")
                f.write(f"username = {username}\n")
                f.write(f"password = {encrypted_password}\n")
                f.write(f"key_file = {key_name}\n")
                f.write(f"timestamp = {datetime.utcnow().isoformat()}Z\n")

            return {'payload': {'status': 'success', 'key_file': key_name}, 'status': 200}

        except Exception as e:
            write_debug({"error": str(e)})
            return {'payload': {'error': str(e)}, 'status': 500}

    def handleStream(self, handle, in_string):
        raise NotImplementedError("Streaming not implemented")

    def done(self):
        pass
