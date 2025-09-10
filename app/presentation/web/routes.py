"""
Rutas web para la interfaz de usuario
Implementa el patrón MVC para la presentación web
"""
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# Configuración de templates 
templates = Jinja2Templates(directory="templates")

# Router para rutas web
web_router = APIRouter(tags=["web"])

@web_router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Página principal del generador de horarios
    Implementa el patrón Controller para la vista principal
    """

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "ScheduleWise - Sistema de Horarios",
            "university": "Universidad de Guadalajara",
            "campus": "CUCEI - Centro Universitario de Ciencias Exactas e Ingenierías"
        }
    )

@web_router.get("/schedule", response_class=HTMLResponse)
async def schedule_view(request: Request):
    """ Vista de horario generado """
    return templates.TemplateResponse(
        "schedule.html",
        {
            "request": request,
            "title": "Mi Horario - CUCEI"
        }
    )