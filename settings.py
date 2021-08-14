import ujson

SETTINGS_JSON = "settings.json"

settings_data = {}

with open(SETTINGS_JSON, "r") as settings_file:
    settings_data = {**ujson.load(settings_file), **settings_data}

DEBUG = settings_data.get("DEBUG", True)
