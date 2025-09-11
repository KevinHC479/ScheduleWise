"""
Entidades de dominio de ScheduleWise
Implementa el patrón Entity y Value Objects de DDD (Domain Driven Design)
"""
from dataclasses import dataclass
from datetime import time, datetime
from typing import List, Optional, Set
from enum import Enum

class DayOfWeek(Enum):
    """ Enum para días de la semana - Value Object """
    MONDAY = "Lunes"
    TUESDAY = "Martes"
    WEDNESDAY = "Miércoles"
    THURSDAY = "Jueves"
    FRIDAY = "Viernes"
    SATURDAY = "Sábado"

class SubjectType(Enum):
    """ Enum para tipos de materias - Value Object """
    LECTURE = "Cátedra"
    LAB = "Laboratorio"
    SEMINAR = "Seminario"
    WORKSHOP = "Taller"

@dataclass
class TimeSlot:
    """
    Value Object que representa un bloque de tiempo
    Inmutable y con validación de reglas de negocio
    """
    start_time: time
    end_time: time
    day: DayOfWeek

    def __post_init__(self):
        """ Validación de reglas de negocio """
        if self.start_time >= self.end_time:
            raise ValueError("El horario de inicio debe ser menor al horario de fin")
    
    def overlaps_with(self, other: 'TimeSlot') -> bool:
        """ Verifica si hay solapamiento con otro TimeSlot"""
        if self.day != other.day:
            return False
        return not (self.end_time <= other.start_time or self.start_time >= other.end_time)
    
    def duration_minutes(self) -> int:
        """ Calcula la duración en minutos """
        start_datetime = datetime.combine(datetime.today(), self.start_time)
        end_datetime = datetime.combine(datetime.today(), self.end_time)
        return int((end_datetime - start_datetime).total_seconds() / 60)

@dataclass
class Subject:
    """
    Entidad que representa una materia académica
    Implementa el patrón Entity con identidad única.
    """
    code: str # Identificador único (ej: "CC101")
    name: str
    credits: int
    subject_type: SubjectType
    professor: str
    available_slots: List[TimeSlot]
    prerequisites: Set[str] = None # Códigos de materias prerrequisito

    def __post_init__(self):
        """ Inicialización y validación """
        if self.prerequisites is None:
            self.prerequisites = set()
        if self.credits <= 0:
            raise ValueError("Los créditos deben ser mayor a 0.")
        if not self.available_slots:
            raise ValueError("La materia debe tener al menos un horario disponible.")

@dataclass
class StudentConstraint:
    """
    Value Object que representa una restriccion del estudiante
    Implementa el patrón Specification para validaciones más complejas
    """    
    constraint_type: str
    description: str
    blocked_time_slots: List[TimeSlot] = None
    min_break_minutes: int = 30
    max_daily_hours: int = 8
    preferred_days: Set[DayOfWeek] = None
    avoid_early_classes: bool = False # NO clases antes de las 9am
    avoid_late_classes: bool = False # NO clases después de las 6pm

    def __post_init__(self):
        if self.blocked_time_slots is None:
            self.blocked_time_slots = []
        if self.preferred_days is None:
            self.preferred_days = set()

@dataclass
class ScheduleSlot:
    """
    Value Object que representa un slot en el horario generado
    """
    subject: Subject
    time_slot: TimeSlot
    classroom: Optional[str] = None

@dataclass
class Schedule:
    """
    Entidad agregada que representa un horario completo
    Implementa el patrón Aggregate Root
    """
    student_id: str
    semester: int
    schedule_slots: List[ScheduleSlot]
    total_credits: int = 0

    def __post_init__(self):
        """ Calcula créditos totales y valida el horario """
        self.total_credits = sum(slot.subject.credits for slot in self.schedule_slots)
        self._validate_schedule()
    
    def _validate_schedule(self):
        """ 
        Valida que el horario no tenga conflictos
        Implementa reglas de negocio complejas
        """
        time_slots = [slot.time_slot for slot in self.schedule_slots]

        # Verificar solapamientos
        for i, slot1 in enumerate(time_slots):
            for slot2 in time_slots[i+1:]:
                if slot1.overlaps_with(slot2):
                    raise ValueError(f"Conflicto de horario detectado entre {slot1} y {slot2}")

    def get_daily_hours(self, day: DayOfWeek) -> int:
        """ Calcula las horas totales de un día específico """
        daily_slots = [slot for slot in self.schedule_slots if slot.time_slot.day == day]
        return sum(slot.time_slot.duration_minutes() for slot in daily_slots) // 60
    
    def has_conflicts(self) -> bool:
        """ Verifica si el horario tiene conflictos """
        try:
            self._validate_schedule()
            return False
        except ValueError:
            return True
