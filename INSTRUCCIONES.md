# Generador de Horarios Inteligente - **ScheduleWise**

## 🚀 Instalación y Configuración

### 1. Crear y activar entorno virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
.\venv\Scripts\Activate.ps1

# Activar entorno virtual (Linux/Mac)
source venv/bin/activate
```

### 2. Instalar dependencias 
```bash
pip install -r requirements.txt
```

### 3. Ejecutar el servidor
```bash
uvicorn app:main:app --reload
```

### 4. Acceder a la aplicación
- **Interfaz Web**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## Características Principales

### ✨ Funcionalidades
- **Optimización Inteligente**: Algoritmo greedy que considera restricciones y preferencias
- **Interfaz Elegante**: UI Moderna con Tailwind CSS
- **API REST**:  Endpoints completos para intergración
- **Restricciones Personalizadas**: Evitar clases tempranas/tardías, break mínimos, etc.
- **Arquitectura Limpia**: Separación de responsabilidades y patrones de diseño

### 🏗️ Arquitectura
```
├── app/
│   ├── core/           # Configuración central
│   ├── domain/         # Entidades y reglas de negocio
│   ├── application/    # Casos de uso y servicios
│   └── presentation/   # Controllers y API endpoints
├── static/            # Archivos estáticos
├── templates/         # Templates HTML
└── tests/            # Pruebas unitarias
```

## Patrones Implementados
1. **Clean Architecture**: Separación en capas (Domanin, Application, Infrastructure, Presentation)
2. **Repository Pattern**: Abstracción de acceso a datos.
3. **Strategy Pattern**: Algoritmos intercambiables de optimización
4. **Factory Pattern**: Creación de objetos complejos
5. **Dependency Injection**: Inyección de dependencias
6. **DTO Pattern**: Objetos de transferencia de datos
7. **Aggregate Root**: Entidades principales del dominio

## 🔧 Uso de la API

### Obtener materias
```bash
POST /api/v1/schedules/generate
Content-Type: application/json

{
  "available_subjects": [...],
  "student_constraints": {
    "min_break_minutes": 30,
    "max_daily_hours": 8,
    "avoid_early_classes": true,
    "avoid_late_classes": false
  },
  "required_subject_codes": ["CC101", "MAT101"]
}
```

## 🧪 Ejectuar Pruebas

```bash
# Ejecutar todas las pruebas
python -m pytest tests/ -v

# Ejecutar con cobertura
python -m pytest tests/--cov=app --cov-report=html
```

## 🎨 Tecnologías Utilizadas

- **Backend**: Python 3.11+, FastAPI, Pydantic
- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **Testing**: Pytest, Pytest-asyncio
- **Arquitectura**: Clean Architecture, DDD patterns

## Ejemplos de Uso

### 1. Uso básico desde la interfaz web
1. Accede a http://127.0.0.1:8000
2. Haz clic en "Cargar Materias de CUCEI"
3. Selecciona las materias que deseas cursar
4. Configura tus restricciones (horarios, breaks, etc.)
5. Haz clic en "Generar Horario Optimizado"

### 2. Uso programático de la API
```python
import requests

# Obtener materias disponibles
response = requests.get("http://127.0.0.1:8000/api/v1/schedules/subjects/cucei")
subjects = response.json()

# Generar horario
payload = {
    "available_subjects": subjects,
    "student_constraints": {
        "min_break_minutes": 30,
        "max_daily_hours": 8,
        "avoid_early_classes": True
    },
    "required_subject_codes": ["CC101", "MAT101"]
}

response = requests.post(
    "http://127.0.0.1:8000/api/v1/schedules/generate",
    json=payload
)
schedule = response.json()
```

## 🔍 Algoritmo de Optimización 

El sistema utiliza un **algoritmo greedy** que:

1. **Filtra** materias requeridas y disponibles
2. **Genera** combinaciones inteligentes priorizando materias con menos opciones
3. **Evalúa** cada combinación considerando:
    - Conflictos de horario
    - Restricciones del estudiante
    - Distribución equilibrada de carga
    - Breaks adecuados entre clases
4. **Selecciona** el horario con mejor score de optimización

### Criterios de Optimización
- ✅ Sin conflictos de horario
- ✅ Respeto a restricciones personales
- ✅ Distribución equilibrada por día
- ✅ Breaks mínimos entre clases
- ✅ Preferencias de horario (evitar muy temprano/tarde)

## 🚀 Próximas Mejoras

- [ ] Algoritmo genético para optimización avanzada
- [ ] Persistencia en base de datos
- [ ] Autenticación de usuarios
- [ ] Exportación a PDF/iCal
- [ ] Notificaciones de cambios de horario
- [ ] Integración con sistemas académicos

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

**Desarrollado con ❤️ para TODOS los estudiantes :D**