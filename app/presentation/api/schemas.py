"""
Esquemas Pydantic para validación de la API.
Implementa el patrón DTO (Data Transfer Object) para la capa de presentación
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Set
from datetime import time
from enum import Enum

from app.domain.entities import ScheduleSlot

class DayOfWeekSchema(str, Enum):
    """ Schema para días de la semana """
    MONDAY = "Lunes"
    TUESDAY = "Martes"
    WEDNESDAY = "Miércoles"
    THURSDAY = "Jueves"
    FRIDAY = "Viernes"
    SATURDAY = "Sábado"

class SubjectTypeSchema(str, Enum):
    """ Schema para tipos de materia """
    LECTURE = "Cátedra"
    LAB = "Laboratorio"
    SEMINAR = "Seminario"
    WORKSHOP = "Taller"

class TimeSlotSchema(BaseModel):
    """
    Schema para bloques de tiempo
    Incluye validaciones de negocio en la capa de presentación
    """
    start_time: str = Field(..., description="Hora de inicio en formato HH:MM")
    end_time: str = Field(..., description="Hora de fin en formato HH:MM")
    day: DayOfWeekSchema = Field(..., description="Día de la semana")

    @validator('start_time', 'end_time')
    def validate_time_format(cls, v):
        """ Valida formato de tiempo HH:MM """
        try:
            time.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError("Formato de tiempo inválido. Use HH:MM")
    @validator('end_time')
    def validate_end_after_start(cls, v, values):
        """ Valida que la hora de fin sea posterior a la de inicio """
        if 'start_time' in values:
            start = time.fromisoformat(values['start_time'])
            end = time.fromisoformat(v)
            if end <= start:
                raise ValueError("La hora de fin debe ser posterior a la de inicio")
        return v

class SubjectSchema(BaseModel):
    """ Schema para materias académicas """
    code: str = Field(..., min_length=2, max_length=10, description="Código de la materia")
    name: str = Field(..., min_length=3, max_length=100, description="Nombre de la materia")
    credits: int = Field(..., ge=1, le=10, description="Número de créditos")
    subject_type: SubjectTypeSchema = Field(..., min_items=1, description="Horarios disponibles")
    professor: str = Field(..., min_length=3, max_length=100, description="Nombre del profesor")
    available_slots: List[TimeSlotSchema] = Field(..., min_items=1, description="Horarios disponibles")
    prerequisites: Optional[Set[str]] = Field(default=set(), description="Códigos de materias prerequisito")

class StudentConstraintSchema(BaseModel):
    """ Schema para restricciones del estudiante """
    constraint_type: str = Field(default="general", description="Tipo de restriccion")
    description: str = Field(default="Restricciones generales", description="Descripcion de las restricciones")
    blocked_time_slots: Optional[List[TimeSlotSchema]] = Field(default=[], description="Horarios bloqueados")
    min_break_minutes: int = Field(default=30, ge=0, le=120, description="Minutos mínimos de descanso")
    max_daily_hours: int = Field(default=8, ge=1, le=12, description="Máximo de horas diarias")
    preferred_days: Optional[Set[DayOfWeekSchema]] = Field(default=set(), description="Dias preferidos")
    avoid_early_classes: bool = Field(default=False, description="Evitar clases antes de las 9am")
    avoid_late_classes: bool = Field(default=False, description="Evitar clases después de las 6pm")

class ScheduleRequestSchema(BaseModel):
    """ Schema para solicitud de generación de horario """
    available_subjects: List[SubjectSchema] = Field(..., min_items=1, description="Materias discponibles")
    student_constraints: StudentConstraintSchema = Field(..., description="Restricciones del estudiante")
    required_subject_codes: Set[str] = Field(..., min_items=1, description="Códigos de materias requeridas")

    @validator('required_subject_codes')
    def validate_required_subjects_exist(cls, v, values):
        """ Valida que las materias requeridas existan en las disponibles """
        if 'available_subjects' in values:
            available_codes = {subject.code for subject in values['available_subjects']}
            missing = v - available_codes
            if missing:
                raise ValueError(f"Materias requeridas no encontradas: {missing}")
        return v

class ScheduleSlotSchema(BaseModel):
    """ Schema para slots del horario generado """
    subject: SubjectSchema
    time_slot: TimeSlotSchema
    classroom: Optional[str] = Field(None, description="Aula asignada") 

class ScheduleResponseSchema(BaseModel):
    """ Schema para respuesta de horario generado """
    student_id: str = Field(..., description="ID del estudiante")
    semester: str = Field(..., description="Semestre académico")
    schedule_slots: List[ScheduleSlotSchema] = Field(..., description="Slots del horario")
    total_credits: int = Field(..., ge=0, description="Total de créditos")
    generation_timestamp: str = Field(..., description="Timestamp de generación")
    optimization_score: Optional[float] = Field(None, description="Score de optimización")

class ErrorResponseSchema(BaseModel):
    """ Schema para respuestas de error """
    error: str = Field(..., description="Tipo de error")
    message: str = Field(..., description="Mensaje de error")
    details: Optional[dict] = Field(None, description="Detalles adicionales del error")

class SuccessResponseSchema(BaseModel):
    """ Schema para respuestas exitosas """
    success: bool = Field(True, description="Indicador de éxito")
    message: str = Field(..., description="Mensaje de éxito")
    data: Optional[dict] = Field(None, description="Datos adicionales")
