# Generador de Horarios **Schedule Wise**

Sistema inteligente para generar horarios académicos optimizados según parámetros seleccionables.

## Características

- 🎯 **Optimización Inteligente**: Algoritmo que considera preferencias y restricciones
- 📅 **Interfaz Elegante**: UI moderna con TailwindCSS
- ⚡ **API Rápida**: Backend con FastAPI
- 🏗️ **Arquitectura Limpia**: Separación de responsabilidades y patrones de diseño
- 📱 **Responsive**: Diseño adaptable a dispositivos móviles

## Tecnologías

- **Backend**: Python 3.11+, FastAPI, Pydantic
- **Frontend**: HTML5, TailwindCSS, CSS puro, JavaScript
- **Algoritmos**: Optimización con restricciones
- **Arquitectura**: Clean Architecture, Repository Pattern, Dependency Injection

## Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor de desarrollo
uvicorn app.main:app --reload
```

## Uso

1. Accede a `http://localhost:8000`, luego de ejecturar el servidor de desarrollo
2. Introduce tus materias disponibles
3. Define tu disponibilidad de tiempo
4. Establece restricciones personales
5. Genera tu horario óptimo

## Estructura del Proyecto

```
├── app/
│   ├── core/           # Configuración y utilidades centrales
│   ├── domain/         # Entidades y reglas de negocio
│   ├── infrastructure/ # Implementaciones concretas
│   ├── application/    # Casos de uso y servicios
│   └── presentation/   # Controllers y API endpoints
├── static/            # Archivos estáticos (CSS, JS)
├── templates/         # Templates HTML
└── tests/            # Pruebas unitarias
```
