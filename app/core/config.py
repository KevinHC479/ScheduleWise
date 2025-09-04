"""
Configuración centralizada de la aplicación
Implementa el patrón Singleton para configuración global
"""
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """
    Clase de configuración usando Pydantic Settings
    Implementa el patrón Configuration Object para centralizar la configuración global.
    """

    # Configuración del servidor
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = True
    
    # Configuración específica de CUCEI
    university_name: str = "Universidad de Guadalajara"
    campus_name: str = "CUCEI - Centro Universitario de Ciencias Exactas e Ingenierías"

    # Horarios académicos estándar de CUCEI
    class_start_times: List[str] = [
        "07:00", "08:00", "09:00", "10:00", "11:00",
        "12:00", "13:00", "14:00", "15:00", "16:00",
        "17:00", "18:00", "19:00", "20:00", "21:00"
    ]

    # Duración estándar de las clases en minutos
    class_duration_minutes:int = 55
    break_duration_minutes:int = 5

    # Dias de la semana académicos
    academic_days: List[str] = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado"]

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache
def get_settings() -> Settings:
    """
    Factory function con cache para obtener configuración.
    Implementa el patrón Singleton usando lru_cache.
    """
    return Settings()
