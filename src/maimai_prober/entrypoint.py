import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from maimai_prober import sessions
from maimai_prober.loggings import Ansi, log
from maimai_prober.settings import get_settings

settings = get_settings()


@asynccontextmanager
async def init_lifespan(asgi_app: FastAPI):
    asyncio.create_task(sessions.maimai_client.songs())
    await sessions.init_db()
    yield  # Above: Startup process Below: Shutdown process
    await sessions.async_engine.dispose()


def init_routes(asgi_app: FastAPI) -> None:
    from maimai_prober.routes import router  # noqa: F401

    @asgi_app.get("/", include_in_schema=False)
    async def root():
        return {"message": "Welcome to Maimai Prober API. Visit /docs for API documentation."}

    asgi_app.include_router(router)


def init_api() -> FastAPI:
    """Create & initialize our app."""
    asgi_app = FastAPI(lifespan=init_lifespan)

    init_routes(asgi_app)

    return asgi_app


asgi_app = init_api()


def main():
    log(f"Uvicorn running on http://{settings.bind_host}:{str(settings.bind_port)} (Press CTRL+C to quit)", Ansi.YELLOW)
    uvicorn.run("maimai_prober.entrypoint:asgi_app", port=settings.bind_port, host=settings.bind_host)


if __name__ == "__main__":
    main()
