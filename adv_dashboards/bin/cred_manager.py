  GNU nano 7.2                                                          hello_world.py                                                                   import json
import os
import uuid
import re
from collections import defaultdict
from datetime import datetime
from cryptography.fernet import Fernet
from splunk.persistconn.application import PersistentServerConnectionApplication

SPLUNK_HOME = os.environ.get("SPLUNK_HOME", "/opt/splunk")
APP_NAME = "search"
APP_DIR = os.path.join(SPLUNK_HOME, "etc", "apps", APP_NAME)
CONFIG_PATH = os.path.join(APP_DIR, "local", "credential.conf")
KEY_DIR = os.path.join(APP_DIR, "etc", "auth")
DEBUG_FILE = os.path.join(APP_DIR, "var", "log", "debug_input.txt")

def parse_servers_from_form(form_data):
    servers = defaultdict(dict)
    pattern = re.compile(r"servers\[(\d+)\]\[(\w+)\]")

    for key, value in form_data:
        match = pattern.match(key)
        if match:
            index, field = match.groups()
            servers[int(index)][field] = value

    # Convert defaultdict to list of dicts, ordered by index
    return [servers[i] for i in sorted(servers.keys())]

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
            write_debug({"instring:": in_string})
            req = json.loads(in_string)
            write_debug({"json req: ": req})

            form_data = req.get("form", [])
            servers = parse_servers_from_form(form_data)


            #servers = req.get("servers", [])
            write_debug({"raw_input": in_string, "parsed_servers": servers})

            if not servers:
                return {'payload': {'error': 'No servers provided'}, 'status': 400}

            key_name, key = get_or_create_key()
            fernet = Fernet(key)

            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, "w") as f:
                f.write("[settings]\n")
                for server in servers:
                    prefix = server.get("type")
                    if not prefix:
                        continue
                    url = server.get("url", "")
                    username = server.get("username", "")
                    password = server.get("password", "")
                    if not all([url, username, password]):
                        continue
                    encrypted_password = fernet.encrypt(password.encode()).decode()

                    f.write(f"{prefix}_url = {url}\n")
                    f.write(f"{prefix}_username = {username}\n")
                    f.write(f"{prefix}_password = {encrypted_password}\n")

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