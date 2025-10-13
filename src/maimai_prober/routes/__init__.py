from fastapi import APIRouter, Depends, Security
from fastapi.security import APIKeyHeader

from maimai_prober import sessions
from maimai_prober.exceptions import LeporidException
from maimai_prober.routes import developers, included

router = APIRouter()
settings = sessions.get_settings()

api_key_header = APIKeyHeader(name="x-developer-token", auto_error=False)


async def require_developer_token(api_key: str | None = Security(api_key_header)):
    if api_key is not None:
        if api_key in sessions.enabled_developer_tokens:
            return api_key
        raise LeporidException.INVALID_CREDENTIALS.with_detail("Invalid developer token")
    raise LeporidException.INVALID_CREDENTIALS.with_detail("Missing developer token")


dependencies = []
if settings.enable_developer_check:
    dependencies.append(Depends(require_developer_token))

router.include_router(included.router, dependencies=dependencies)
if settings.enable_developer_apply and settings.enable_developer_check:
    router.include_router(developers.router)
