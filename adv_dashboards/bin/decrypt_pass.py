import os
import base64
import configparser
from cryptography.fernet import Fernet

# Paths
CONFIG_PATH = "./local/credential.conf"
KEYS_DIR = "./etc/auth/"

def load_config(path):
    config = configparser.ConfigParser()
    config.read(path)
    return config['settings']

def load_key(key_file):
    key_path = os.path.join(KEYS_DIR, f"{key_file}")
    if not os.path.exists(key_path):
        raise FileNotFoundError(f"Key file not found: {key_path}")
    with open(key_path, 'rb') as f:
        return f.read()

def decrypt_password(encrypted_b64, key_b64):
    try:
        print(f"Encrypted password: {encrypted_b64}")
        print(f"Base64 key: {key_b64}")

        fernet = Fernet(key_b64)
        decrypted = fernet.decrypt(encrypted_b64.encode()).decode()
        return decrypted

    except Exception as e:
        print("ERROR: Failed to decrypt password:", str(e))
        return None


def main():
    config = load_config(CONFIG_PATH)
    key_file = config.get("key_file")
    encrypted_password = config.get("password")

#temp
    print(f"Config: {config}")
    print(f"key_file: {key_file}")
    print(f"password: {encrypted_password}")

    if not key_file or not encrypted_password:
        print("Missing key_id or encrypted password in config.")
        return

    try:
        key = load_key(key_file)
    except FileNotFoundError as e:
        print(f"WARNING: {e}")
        return

    try:
        password = decrypt_password(encrypted_password, key)
        print(f"Decrypted password: {password}")
    except Exception as e:
        print(f"ERROR: Failed to decrypt password: {e}")

if __name__ == "__main__":
    main()

