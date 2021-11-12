import os

import ujson

SETTINGS_JSON = "settings.json"

settings_data = {
    "POSTGRES_USER": os.getenv("POSTGRES_USER", "postgres"),
    "POSTGRES_DB": os.getenv("POSTGRES_DB", "postgres"),
    "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
    "POSTGRES_HOST": os.getenv("POSTGRES_HOST", "localhost"),
    "POSTGRES_PORT": os.getenv("POSTGRES_PORT", 5432),
}

with open(SETTINGS_JSON, "r") as settings_file:
    settings_data = {**ujson.load(settings_file), **settings_data}

DEBUG = settings_data.get("DEBUG", True)

PSQL_CONN = (
    f"""postgres://{settings_data['POSTGRES_USER']}:"""
    f"""{settings_data['POSTGRES_PASSWORD']}@"""
    f"""{settings_data['POSTGRES_HOST']}:"""
    f"""{settings_data['POSTGRES_PORT']}/"""
    f"""{settings_data['POSTGRES_DB']}"""
)
DB_CONNECTION = {
    "mongo": settings_data.get("MONGO_CONNECTION", "mongodb://localhost:27017"),
    "postgres": settings_data.get("PSQL_CONNECTION", PSQL_CONN),
}
