from fastapi import APIRouter
from maimai_py import MaimaiRoutes, PlayerIdentifier

from maimai_prober.providers.usagicard import UsagiCardProvider
from maimai_prober.sessions import maimai_client
from maimai_prober.settings import get_settings

router = APIRouter()
settings = get_settings()

routes = MaimaiRoutes(
    maimai_client,
    settings.lxns_developer_token,
    settings.divingfish_developer_token,
    settings.arcade_proxy,
)

# add included routes in maimai_py
router.include_router(routes.get_router(routes._dep_hybrid, skip_base=False), tags=["base"])
router.include_router(routes.get_router(routes._dep_divingfish, routes._dep_divingfish_player), prefix="/divingfish", tags=["divingfish"])
router.include_router(routes.get_router(routes._dep_lxns, routes._dep_lxns_player), prefix="/lxns", tags=["lxns"])
router.include_router(routes.get_router(routes._dep_wechat, routes._dep_wechat_player), prefix="/wechat", tags=["wechat"])
router.include_router(routes.get_router(routes._dep_arcade, routes._dep_arcade_player), prefix="/arcade", tags=["arcade"])

# add usagicard route
router.include_router(
    routes.get_router(lambda: UsagiCardProvider(), lambda uuid: PlayerIdentifier(credentials=uuid)), prefix="/usagicard", tags=["usagicard"]
)

# add update chain route
router.include_router(
    routes.get_updates_chain_route(
        source_deps=[
            ("divingfish", routes._dep_divingfish),
            ("lxns", routes._dep_lxns),
            ("wechat", routes._dep_wechat),
            ("arcade", routes._dep_arcade),
        ],
        target_deps=[
            ("divingfish", routes._dep_divingfish),
            ("lxns", routes._dep_lxns),
            ("usagicard", lambda: UsagiCardProvider()),
        ],
        source_mode="fallback",
        target_mode="parallel",
    ),
    prefix="/utils",
    tags=["utils"],
)
