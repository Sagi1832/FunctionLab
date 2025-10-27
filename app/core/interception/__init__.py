# app/core/interception/__init__.py

from app.core.interception.x_interception import x_intercepts as x_interception, x_intercepts
from app.core.interception.y_interception import y_intercept as y_interception, y_intercept

# תאימות לשמות "API" ישנים/נוחים
find_x_intercepts = x_interception
find_y_intercepts = y_interception

__all__ = [
    "x_interception", "y_interception",
    "find_x_intercepts", "find_y_intercepts",
    "x_intercepts", "y_intercept",
]
