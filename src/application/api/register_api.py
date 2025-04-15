from fastapi import FastAPI
from application.api.endpoints.portfolio import portfolio
from src.application.api.endpoints import health


routes = [portfolio.router, health.router]


def register_api_routes(app: FastAPI, prefix: str):
    for route in routes:
        app.include_router(route, prefix=prefix)
    return app.routes
