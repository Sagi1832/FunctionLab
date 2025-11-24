from .auth_routers.auth_router import router as auth_router
from .func_library.asymptotes_holes_route import router as asymptotes_and_holes_router
from .func_library.extrema_and_mono import router as extrema_and_mono_router
from .func_library.foundation_funcs.derivative_route import router as derivative_router
from .func_library.foundation_funcs.domain_route import router as domain_router
from .func_library.interceptions import router as interceptions_router
from .llm_route import router as llm_router

routers = [
    auth_router,
    llm_router,
    domain_router,
    derivative_router,
    interceptions_router,
    asymptotes_and_holes_router,
    extrema_and_mono_router,
]

__all__ = [
    "routers",
    "auth_router",
    "llm_router",
    "domain_router",
    "derivative_router",
    "interceptions_router",
    "asymptotes_and_holes_router",
    "extrema_and_mono_router",
]