import uvicorn

from application.settings import settings


async def run_api_server():
    """Запускает FastAPI сервер"""
    config = uvicorn.Config(
        "src.application.app:create_app",
        host="0.0.0.0",
        port=8000,
        log_level="debug" if settings.DEBUG else "info",
        reload=settings.DEBUG,
    )
    server = uvicorn.Server(config)
    await server.serve()
