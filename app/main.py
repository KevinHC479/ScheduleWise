"""
Punto de entrada principal de la aplicación FastAPI
Implementa el patrón de configuración centralizada y dependency injection 
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
from app.core.config import get_settings
from app.presentation.api.routes import schedule_router
from app.presentation.web.routes import web_router

# Configuración de la aplicación usando el patrón Singleton
settings = get_settings()

# Factory Pattern para crear la aplicación FastAPI
def create_app() -> FastAPI:
    """
    Factory Function que crea y configura la app de FastAPI.
    Implementa el patrón Factory para facilitar testing y configuración
    """
    app = FastAPI(
        title="ScheduleWise - Creador de Horarios",
        description="Plataforma inteligente especializada en la optimización de horarios académicos",
        version="1.0.0"
    )

    # Configuración de archivos estáticos 
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # Registro de routers usando el patrón Router
    app.include_router(schedule_router, prefix="/api/v1")
    app.include_router(web_router)

    return app

# Instancia principal de la app
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )