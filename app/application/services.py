"""
Servicios de aplicación que implementan casos de uso.
Implementa el patrón Service Layer y Strategy Pattern para algoritmos
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Set
import itertools
from datetime import time

from app.domain.entities import (
    Subject, StudentConstraint, Schedule, ScheduleSlot, 
    TimeSlot, DayOfWeek, SubjectType
)

class ScheduleOptimizer(ABC):
    """
    Interfaz abstracta para algoritmos de optimización
    Implementa el patrón Strategy para intercambiar algoritmos
    """

    @abstractmethod
    def optimize(
        self, 
        subjects: List[Subject],
        constraints: StudentConstraint,
        required_subjects: Set[str]
    ) -> Optional[Schedule]:
        """ Genera un horario optimizado basado en restricciones """
        pass
    
class GreedyScheduleOptimizer(ScheduleOptimizer):
    """
    Implementación concreta usando el algoritmo greedy
    Optimiza por prioridad: menos conflictos, más créditos, mejor distribucion
    """

    def optimize(
        self, 
        subjects: List[Subject],
        constraints: StudentConstraint,
        required_subjects: Set[str]
    ) -> Optional[Schedule]:
        """
        Algoritmo greedy que selecciona materias por prioridad.
        1. Filtra materias requeridas
        2. Elimina conflictos de restricciones.
        3. Optimiza distribución temporal.
        """
        # Filtra materias requeridas y disponibles
        available_subjects = [
            subject for subject in subjects
            if subject.code in required_subjects
        ]
        
        if not available_subjects:
            return None

        # Genera TODAS las combinaciones posibles de horarios
        best_schedule = None
        best_score = -1

        for subject_combination in self._generate_combinations(available_subjects):
            schedule_slots = []

            # Intentar asignar cada materia
            for subject in subject_combination:
                best_slot = self._find_best_slot(subject, schedule_slots, constraints)
                if best_slot:
                    schedule_slots.append(ScheduleSlot(subject, best_slot))
            
            # Evaluar la calidad de horario
            if schedule_slots:
                try:
                    schedule = Schedule("student", "2024-A", schedule_slots)
                    score = self._calculate_schedule_score(schedule, constraints)

                    if score > best_score:
                        best_score = score
                        best_schedule = schedule
                except ValueError:
                    continue
        return best_schedule

    def _generate_combinations(self, subjects: List[Subject]) -> List[List[Subject]]:
        """
        Genera combinaciones inteligentes de materias 
        Prioriza materias con menos opciones de horario
        """
        # Ordenar la disponibilidad (menos opciones primero)
        sorted_subjects = sorted(subjects, key=lambda s: len(s.available_slots))

        # Generar combinaciones de diferentes tamaños
        combinations = []

        for r in range(1, min(len(sorted_subjects) + 1, 8)): # Máximo 7 materias
            combinations.extend(itertools.combinations(sorted_subjects, r)) 
        
        return [list(combo) for combo in combinations]
    
    def _find_best_slot(
        self,
        subject: Subject,
        existing_slots: List[ScheduleSlot],
        constraints: StudentConstraint
    ) -> Optional[TimeSlot]: 
        """
        Encuentra el mejor slot para una materia considerando restricciones
        """
        existing_time_slots = [slot.time_slot for slot in existing_slots]

        # Filtrar slots que no conflicten
        valid_slots = []
        for slot in subject.available_slots:
            if self._is_slot_valid(slot, existing_time_slots, constraints):
                valid_slots.append(slot)

        if not valid_slots:
            return None

        # Seleccionar el mejor slot basado en preferencias
        return self._rank_slots(valid_slots, constraints)[0]

    def _is_slot_valid(
        self,
        slot: TimeSlot,
        existing_slots: List[TimeSlot],
        constraints: StudentConstraint
    ) -> bool:
        """ Valida si un slot cumple con todas las restricciones """
        
        # Verificar solapamientos
        for existing_slot in existing_slots:
            if slot.overlaps_with(existing_slot):
                return False
        
        # Verificar restricciones de tiempo bloqueado
        for blocked_slot in constraints.blocked_time_slots:
            if slot.overlaps_with(blocked_slot):
                return False

        # Verificar restriccion de clases tempranas
        if constraints.avoid_early_classes and slot.start_time < time(9, 0):
            return False

        # Verificar restriccion de clases tardias
        if constraints.avoid_late_classes and slot.start_time > time(18, 0):
            return False
        
        return True

    def _rank_slots(self, slots: List[TimeSlot], constraints: StudentConstraint) -> List[TimeSlot]:
        """
        Rankea slots por preferencia del estudiante
        Implementa heurísticas de optimización
        """
        def slot_score(slot: TimeSlot) -> float:
            score = 0.0

            # Preferir días específicos
            if slot.day in constraints.preferred_days:
                score += 10.0
            
            # Preferir horarios intermedios (10am - 4pm)
            if time(10, 0) <= slot.start_time <= time(16,0):
                score += 5.0
            
            # Penalizar horarios muy tempranos o muy tardíos
            if slot.start_time <= time(8,0) or slot.start_time > time(19,0):
                score -= 3.0
            
            return score
        
        return sorted(slots, key=slot_score, reverse=True)


    def _calculate_schedule_score(self, schedule: Schedule, constraints: StudentConstraint) -> float:
        """
        Calcula un score de calidad para el horario
        Considera múltiples factores de optimización
        """

        score = 0.0

        # Score base por créditos
        score += schedule.total_credits * 10

        # Penalizar días con muchas horas
        for day in DayOfWeek:
            daily_hours = schedule.get_daily_hours(day)
            if daily_hours > constraints.max_daily_hours:
                score -= (daily_hours - constraint.max_daily_hours) * 5
        
        # Bonificar distribución equilibrada
        daily_hours = [schedule.get_daily_hours(day) for day in DayOfWeek]
        if daily_hours:
            # Menor desviación estándar = mejor distribución
            avg_hours = sum(daily_hours) / len(daily_hours)
            variance = sum((h - avg_hours) ** 2 for h in daily_hours) / len(daily_hours)
            score += max(0, 10 - variance)
        
        # Bonificar breaks adecuados entre clases
        score += self._calculate_break_score(schedule, constraints)

        return score
    
    def _calculate_break_score(self, schedule: Schedule, constraints: StudentConstraint) -> float:
        """
        Calcula score basado en breaks entre clases
        """
        break_score = 0.0

        # Agrupar por día
        daily_slots = {}
        for slot in schedule.schedule_slots:
            day = slot.time_slot.day
            if day not in daily_slots:
                daily_slots[day] = []
            daily_slots[day].append(slot.time_slot)

        # Evaluar breaks en cada día
        for day_slots in daily_slots.values():
            if len(day_slots) < 2:
                continue
            
            # Ordenar por hora de inicio
            scored_slots = sorted(day_slots, key=lambda s: s.start_time)

            # Calcular breaks entre clases consecutivas
            for i in range(len(sorted_slots) - 1):
                current_end = sorted_slots[i].end_time
                next_start = sorted_slots[i + 1].start_time

                # Calcular minutos de break
                break_minutes = (
                    (next_start.hour * 60 + next_start.minute) - 
                    (current_end.hour * 60 + current_end.minute)
                )

                # Evaluar calidad del break
                if break_minutes >= constraints.min_break_minutes:
                    break_score += 2.0
                elif break_minutes > 0:
                    break_score += 1.0
                else:
                    break_score -= 5.0 # Penalizar clases consecutivas sin break

        return break_score

class ScheduleGeneratorService:
    """
    Servicio principal para la generación de horarios
    Implementa el patrón Facade para simplificar la interfaz
    """

    def __init__(self, optimizer: ScheduleOptimizer = None):
        """
        Constructor con dependency injection
        Permite intercambiar algoritmos de optimización
        """            

        self.optimizer = optimizer or GreedyScheduleOptimizer() 
    
    def generate_schedule(
        self,
        available_subjects: List[Subject],
        student_constraints: StudentConstraint,
        required_subject_codes: Set[str]
    ) -> Optional[Schedule]:
        """
        Caso de uso principal: generar horario optimizado
        """

        if not required_subject_codes:
            raise ValueError("Debe seleccionar al menos una materia")

        # Validar que las materias requeridas existen
        availabre_codes = {subject.code for subject in available_subjects}
        missing_subjects = required_subject_codes - availabre_codes

        if missing_subjects:
            raise ValueError(f"Materias no encontradas: {missing_subjects}")

        # Generar horario optimizado
        schedule = self.optimizer.optimize(
            available_subjects,
            student_constraints,
            required_subject_codes
        )
        
        return schedule
        