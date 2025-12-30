"""
Vercel Serverless Function Entry Point

This file adapts the FastAPI application to work with Vercel's serverless platform.
All routes from src.api.main are exposed through this entry point.
"""

from src.api.main import app

# Vercel expects the ASGI application to be named 'app'
# Our FastAPI app from src.api.main is already named 'app', so we just import it

# This allows Vercel to handle all requests through the FastAPI application
