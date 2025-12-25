"""Routes package."""

from . import health_routes
from . import file_routes
from . import generation_routes
from . import chat_routes

__all__ = [
    'health_routes',
    'file_routes',
    'generation_routes',
    'chat_routes',
]
