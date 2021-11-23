import os

import ujson

SETTINGS_JSON = "settings.json"
dir_name = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.abspath(os.path.join(dir_name, SETTINGS_JSON))


settings_data = {
    "POSTGRES_USER": os.getenv("POSTGRES_USER", "postgres"),
    "POSTGRES_DB": os.getenv("POSTGRES_DB", "postgres"),
    "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
    "POSTGRES_HOST": os.getenv("POSTGRES_HOST", "localhost"),
    "POSTGRES_PORT": os.getenv("POSTGRES_PORT", 5432),
}

with open(SETTINGS_PATH, "r") as settings_file:
    settings_data = {**ujson.load(settings_file), **settings_data}

DEBUG = settings_data.get("DEBUG", True)

PSQL_CONN = (
    # Will throw:
    # sqlalchemy.exc.NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:postgres
    # See: https://stackoverflow.com/a/64698899/2290820
    f"""postgresql://{settings_data['POSTGRES_USER']}:"""
    f"""{settings_data['POSTGRES_PASSWORD']}@"""
    f"""{settings_data['POSTGRES_HOST']}:"""
    f"""{settings_data['POSTGRES_PORT']}/"""
    f"""{settings_data['POSTGRES_DB']}"""
)
DB_CONNECTION = {
    "mongo": settings_data.get("MONGO_CONNECTION", "mongodb://localhost:27017"),
    "postgres": settings_data.get("PSQL_CONNECTION", PSQL_CONN),
}
