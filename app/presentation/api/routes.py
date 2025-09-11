"""
Rutas de la API REST
Implementa el patrón Controller para manejar requests HTTP
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime, time

from app.presentation.api.schemas import (
    ScheduleRequestSchema, ScheduleResponseSchema, 
    ErrorResponseSchema, SuccessResponseSchema, 
    SubjectSchema, TimeSlotSchema, StudentConstraintSchema
)

from app.application.services import ScheduleGeneratorService
from app.domain.entities import (
    Subject, StudentConstraint, TimeSlot, DayOfWeek, SubjectType
)

# Router principal para endpoints de horarios
schedule_router = APIRouter(prefix="/schedules", tags=["schedules"])

def get_schedule_service() -> ScheduleGeneratorService:
    """
    Dependency injection para el servicio de horarios
    Implementa el patrón Factory para crear servicios
    """

    return ScheduleGeneratorService()

@schedule_router.post(
    "/generate",
    response_model=ScheduleResponseSchema,
    responses={
        400: {"model": ErrorResponseSchema},
        422: {"model": ErrorResponseSchema},
        500: {"model": ErrorResponseSchema}
    },
    summary="Generar horario optimizado",
    description="Genera un horario académico optimizado basado en materias disponibles y restricciones del estudiante"
)
async def generate_schedule(
    request: ScheduleRequestSchema,
    service: ScheduleGeneratorService = Depends(get_schedule_service)
) -> ScheduleResponseSchema:
    """
    Endponint principal para generar horarios
    Implementa el patrón CommandHandler
    """
    try:
        # Convertir DTOs a entidades de dominio
        subjects = _convert_subjects_to_domain(request.available_subjects)
        constraints = _convert_constraints_to_domain(request.student_constraints)

        # Ejecutar caso de uso
        schedule = service.generate_schedule(
            subjects,
            constraints,
            request.required_subject_codes
        )

        if not schedule:
            raise HTTPException(
                status_code=400,
                detail="No se pudo generar un horario válido con las restricciones proporcionadas"
            )

        # Convertir resultado a DTO de respuesta
        return _convert_schedule_to_response(schedule)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@schedule_router.get(
    "/subjects/cucei",
    response_model=List[SubjectSchema],
    summary="Obtener materias de CUCEI",
    description="Retorna un catálogo de materias disponibles en CUCEI con sus horarios"
)
async def get_cucei_subjects() -> List[SubjectSchema]:
    """
    Endpoint para obtener materias predefinidas de CUCEI
    Simula una base de datos de materias, por el momento
    """

    # Datos de ejemplo de materias de CUCEI
    sample_subjects = [
        {
            "code": "CC101",
            "name": "Programación I",
            "credits": 8,
            "subject_type": "Cátedra",
            "professor": "Dr. García López",
            "available_slots": [
                {"start_time": "08:00", "end_time": "10:00", "day": "Lunes"},
                {"start_time": "08:00", "end_time": "10:00", "day": "Miércoles"},
                {"start_time": "10:00", "end_time": "12:00", "day": "Martes"},
                {"start_time": "10:00", "end_time": "12:00", "day": "Jueves"}
            ],
            "prerequisites": set()
        },
        {
            "code": "CC102",
            "name": "Estructuras de Datos",
            "credits": 8,
            "subject_type": "Cátedra",
            "professor": "Dra. Martínez Silva",
            "available_slots": [
                {"start_time": "14:00", "end_time": "16:00", "day": "Lunes"},
                {"start_time": "14:00", "end_time": "16:00", "day": "Miércoles"},
                {"start_time": "16:00", "end_time": "18:00", "day": "Martes"},
                {"start_time": "16:00", "end_time": "18:00", "day": "Jueves"}
            ],
            "prerequisites": {"CC101"}
        },
        {
            "code": "MAT101",
            "name": "Cálculo Diferencial",
            "credits": 8,
            "subject_type": "Cátedra",
            "professor": "Dr. Rodríguez Pérez",
            "available_slots": [
                {"start_time": "07:00", "end_time": "09:00", "day": "Lunes"},
                {"start_time": "07:00", "end_time": "09:00", "day": "Miércoles"},
                {"start_time": "09:00", "end_time": "11:00", "day": "Martes"},
                {"start_time": "09:00", "end_time": "11:00", "day": "Jueves"}
            ],
            "prerequisites": set()
        },
        {
            "code": "FIS101",
            "name": "Física I",
            "credits": 8,
            "subject_type": "Cátedra",
            "professor": "Dr. Hernández Castro",
            "available_slots": [
                {"start_time": "12:00", "end_time": "14:00", "day": "Lunes"},
                {"start_time": "12:00", "end_time": "14:00", "day": "Miércoles"},
                {"start_time": "14:00", "end_time": "16:00", "day": "Viernes"}
            ],
            "prerequisites": {"MAT101"}
        },
        {
            "code": "LAB101",
            "name": "Laboratorio de Programación",
            "credits": 4,
            "subject_type": "Laboratorio",
            "professor": "Ing. López Morales",
            "available_slots": [
                {"start_time": "16:00", "end_time": "18:00", "day": "Viernes"},
                {"start_time": "18:00", "end_time": "20:00", "day": "Viernes"}
            ],
            "prerequisites": {"CC101"}
        }
    ]

    return [SubjectSchema(**subject) for subject in sample_subjects]

@schedule_router.get(
    "/health",
    response_model=SuccessResponseSchema,
    summary="Health check",
    description="Verifica el estado del servicio de horarios"
)
async def health_check() -> SuccessResponseSchema:
    """ Endpoint de health check """
    return SuccessResponseSchema(
        success=True,
        message="Servicio de horarios funcionando correctamente",
        data={"timestamp": datetime.now().isoformat()}
    )

def _convert_subjects_to_domain(subjects_dto: List[SubjectSchema]) -> List[Subject]:
    """
    Convierte DTOs de materias a entidades de dominio
    Implementa el patrón Mapper
    """

    domain_subjects = []

    for subject_dto in subjects_dto:
        # Convertir time slots
        time_slots = []
        for slot_dto in subject_dto.available_slots:
            time_slot = TimeSlot(
                start_time=time.fromisoformat(slot_dto.start_time),
                end_time=time.fromisoformat(slot_dto.end_time),
                day=DayOfWeek(slot_dto.day.value) ## CORREGIDO
            )
            time_slots.append(time_slot)
        
        # Crear entidad de dominio
        subject = Subject(
            code=subject_dto.code,
            name=subject_dto.name,
            credits=subject_dto.credits,
            subject_type=SubjectType(subject_dto.subject_type.value),
            professor=subject_dto.professor, 
            available_slots=time_slots,
            prerequisites=subject_dto.prerequisites or set()
        )
        domain_subjects.append(subject)

    return domain_subjects

def _convert_constraints_to_domain(constraints_dto: StudentConstraintSchema) -> StudentConstraint:
    """ 
    Convierte DTO de restricciones a entidad de dominio
    """
    # Convertir time slots bloqueados
    blocked_slots = []
    if constraints_dto.blocked_time_slots:
        for slot_dto in constraints_dto.blocked_time_slots:
            time_slot = TimeSlot(
                start_time=time.fromisoformat(slot_dto.start_time),
                end_time=time.fromisoformat(slot_dto.end_time),
                day=DayOfWeek(slot_dto.day.value)
            )
            blocked_slots.append(time_slot)
    
    # Convertir días preferidos
    preferred_days = set()
    if constraints_dto.preferred_days:
        preferred_days = {DayOfWeek(day.value) for day in constraints_dto.preferred_days}

    return StudentConstraint(
        constraint_type=constraints_dto.constraint_type,
        description=constraints_dto.description,
        blocked_time_slots=blocked_slots,
        min_break_minutes=constraints_dto.min_break_minutes,
        max_daily_hours=constraints_dto.max_daily_hours,
        preferred_days=preferred_days,
        avoid_early_classes=constraints_dto.avoid_early_classes,
        avoid_late_classes=constraints_dto.avoid_late_classes
    )

def _convert_schedule_to_response(schedule) -> ScheduleResponseSchema:
    """
    Convierte entidad de horario a DTO de respuesta
    """
    # Convertir slots del horario
    schedule_slots = []
    for slot in schedule.schedule_slots:
        slot_dto = {
            "subject": {
                "code": slot.subject.code,
                "name": slot.subject.name,
                "credits": slot.subject.credits,
                "subject_type": slot.subject.subject_type.value,
                "professor": slot.subject.professor,
                "available_slots": [
                    {
                        "start_time": ts.start_time.strftime("%H:%M"),
                        "end_time": ts.end_time.strftime("%H:%M"),
                        "day": ts.day.value
                    }
                    for ts in slot.subject.available_slots
                ],
                "prerequisites": slot.subject.prerequisites
            },
            "time_slot": {
                "start_time": slot.time_slot.start_time.strftime("%H:%M"),
                "end_time": slot.time_slot.end_time.strftime("%H:%M"),
                "day": slot.time_slot.day.value
            },
        }
        schedule_slots.append(slot_dto)

    return ScheduleResponseSchema(
        student_id=schedule.student_id,
        semester=schedule.semester,
        schedule_slots=schedule_slots,
        total_credits=schedule.total_credits,
        generation_timestamp=datetime.now().isoformat(),
        optimization_score=None # Se puede calcular de ser necesario!!!
    )