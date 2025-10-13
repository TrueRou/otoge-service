import secrets

from fastapi import APIRouter
from sqlmodel import select

from maimai_prober import sessions
from maimai_prober.exceptions import LeporidException
from maimai_prober.models import Developer
from maimai_prober.sessions import async_session_ctx

router = APIRouter(prefix="/developers", tags=["developers"])


@router.post("", response_model=Developer)
async def apply_developer(name: str, description: str | None = None):
    async with async_session_ctx() as session:
        token = secrets.token_hex(16)
        developer = Developer(name=name, token=token, description=description, enabled=False)
        session.add(developer)
        await session.commit()
    return developer


@router.get("", response_model=Developer)
async def get_developer(developer_token: str):
    await sessions.init_developers()
    async with async_session_ctx() as session:
        developer = (await session.exec(select(Developer).where(Developer.token == developer_token))).first()
        return developer
    raise LeporidException.INVALID_CREDENTIALS.with_detail("Invalid developer token")
