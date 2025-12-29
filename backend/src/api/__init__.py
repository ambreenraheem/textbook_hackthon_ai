"""
API module containing all FastAPI routers and endpoints.
"""
from src.api.chat import router as chat_router

__all__ = ["chat_router"]
