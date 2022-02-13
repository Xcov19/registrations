import os

settings_data = {
    "POSTGRES_USER": os.getenv("POSTGRES_USER", "postgres"),
    "POSTGRES_DB": os.getenv("POSTGRES_DB", "postgres"),
    "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
    "POSTGRES_HOST": os.getenv("POSTGRES_HOST", "localhost"),
    "POSTGRES_PORT": os.getenv("POSTGRES_PORT", 5432),
}


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


class StageEnv:
    @classmethod
    def env(cls):
        return cls.__name__.lower()


class Production(StageEnv):
    debug = False
    mongo_uri = settings_data.get("MONGO_CONNECTION")
    postgres_uri = settings_data.get("PSQL_CONNECTION")


class Test(StageEnv):
    debug = True
    mongo_uri = settings_data.get("MONGO_CONNECTION", "mongodb://localhost:27017")
    postgres_uri = settings_data.get("PSQL_CONNECTION", PSQL_CONN)


ENV_CONFIG_DICT = {
    Test.env(): Test,
    Production.env(): Production,
}

ENV_CLASS = ENV_CONFIG_DICT[os.getenv("ENV")]
