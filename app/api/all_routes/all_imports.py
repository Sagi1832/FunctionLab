from .func_library.foundation_funcs.domain_route import router as domain_router
from .func_library.foundation_funcs.limits_route  import router as limits_router
from .func_library.foundation_funcs.need_interval import router as need_interval_router
from .func_library.foundation_funcs.derivative_route import router as derivative_router
from .func_library.interceptions.x_interception_rute import router as x_interception_router
from .func_library.interceptions.y_interception_rute import router as y_interception_router
from .func_library.asymptotes_holes_route import router as asymptotes_and_holes_router
from .func_library.extrema_and_monotonic_route import router as mono_and_critPoints_router


routers = [domain_router, limits_router, need_interval_router, 
            derivative_router, x_interception_router, y_interception_router, 
            asymptotes_and_holes_router, mono_and_critPoints_router]


__all__ = ["routers", "domain_router", "limits_router", 
            "need_interval_router", "derivative_router", "x_interception_router", 
            "y_interception_router", "asymptotes_and_holes_router", "mono_and_critPoints_router"]



