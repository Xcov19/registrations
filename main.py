import asyncio

import fastapi
import uvloop

import settings
import views


app = fastapi.FastAPI(
    debug=settings.ENV_CLASS.debug,
)
app.include_router(views.router)

uvloop.install()

if __name__ == "__main__":
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    config = Config()
    # TODO: fill up config.toml
    config.from_toml("config.toml")
    config.bind = "0.0.0.0:8080"
    asyncio.run(serve(app, config))
