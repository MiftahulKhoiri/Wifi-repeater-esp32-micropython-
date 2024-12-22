import json

CONFIG_FILE = 'wifi_config.json'

def save_config(ssid, password):
    config = {'ssid': ssid, 'password': password}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Kesalahan: {e}")
        return None