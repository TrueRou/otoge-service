from fastapi import APIRouter

from maimai_prober.routes import included

router = APIRouter()

router.include_router(included.router)
