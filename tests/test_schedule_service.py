"""
Pruebas unitarias para el servicio de generación de horarios
Implementa el patrón AAA (Arrange, Act, Assert) y mocking para aislamiento
"""
from operator import truediv
import pytest
from datetime import time
from typing import List

from app.domain.entities import (
    Subject, StudentConstraint, TimeSlot, DayOfWeek, SubjectType
)
from app.application.services import ScheduleGeneratorService, GreedyScheduleOptimizer

class TestScheduleGeneratorService:
    """
    Test suite para el servicio de generación de horarios
    Implementa el patrón Test Class per Class Under Test
    """

    def setup_method(self):
        """
        Setup method que se ejecuta antes de cada test
        Implementa el patrón Test Fixture para preparar datos de prueba
        """

        # Arrange: Preparar datos de prueba
        self.service = ScheduleGeneratorService()

        # Crear materias de prueba
        self.test_subjects = [
            Subject(
                code="CC101",
                name="Programación I",
                credits=8,
                subject_type=SubjectType.LECTURE,
                professor="Dr. García",
                available_slots=[
                    TimeSlot(time(8,0), time(10, 0), DayOfWeek.MONDAY),
                    TimeSlot(time(8,0), time(10, 0), DayOfWeek.WEDNESDAY),
                ]
            ),
            Subject(
                code="MAT101",
                name="Cálculo I",
                credits=8,
                subject_type="Dr. Martínez",
                available_slots=[
                    TimeSlot(time(10,0), time(12,0), DayOfWeek.MONDAY),
                    TimeSlot(time(10,0), time(12, 0), DayOfWeek.WEDNESDAY),
                ]
            )
        ]

        # Crear restricciones de prueba
        self.test_constraints = StudentConstraint(
            constraint_type="test",
            description="Restricciones de prueba",
            min_break_minutes=30,
            max_daily_hours=8,
            avoid_early_classes=False,
            avoid_late_classes=False
        )

    def test_generate_schedule_with_valid_subjects_returns_schedule(self):
        """
        Test: Generar un horario con materias válidas debe retornar un horario
        Impelementa el patrón Given-When-Then
        """
        # Given: Matrias válidas y restricciones
        required_subject = {"CC101", "MAT101"}

        # When: Generar horario
        result = self.service.generate_schedule(
            self.test_subjects,
            self.test_constraints,
            required_subjects
        )

        # Then: Debe retornar un horario válido
        assert result is not None
        assert result.total_credits == 16 # 8 + 8 créditos
        assert len(result.schedule_slots) == 2
        assert not result.has_conflicts()

    def test_generate_schedule_with_empty_subjects_raises_error(self):
        """
        Test: Generar horario sin materias debe lanzar ERROR!!!
        """
        # Given: Lista vacía de materias requeridas
        required_subjects = set()

        # When & Then: Debe lanzar ValueError
        with pytest.raises(ValueError, match="Debe seleccionar al menos una materia"):
            self.service.generate_schedule(
                self.test_subjects,
                self.test_constraints,
                required_subjects
            )

    def test_generate_schedule_with_noexistent_subject_raises_error(self):
        """
        Test: Generar horario con materia inexistente, debe lanzar ERROR
        """
        # Given: Materia que no existe en el catálogo
        required_subjects = {"NOEXISTENT"}

        # When & Then: Debe lanzar ValueError
        with pytest.raises(ValueError, match="Materias no encontradas"):
            self.service.generate_schedule(
                self.test_subjects,
                self.test_constraints,
                required_subjects
            )

class TestGreedyScheduleOptimizer:
    """
    Test suite para el optimizador greedy
    """

    def setup_method(self):
        """ Setup para tests del optimizador """
        self.optimizer = GreedyScheduleOptimizer()

        # Crear materias con conflictos de horario para probar optimización
        self.conflicting_subjects = [
            Subject(
                code="SUBJ1",
                name="Materia 1",
                credits=4,
                subject_type=SubjectType.LECTURE,
                professor="Prof 1",
                available_slots=[
                    TimeSlot(time(8, 0), time(10, 0), DayOfWeek.MONDAY),
                ]
            ),
            Subject(
                code="SUBJ2",
                name="Materia 2",
                credits=4,
                subject_type=SubjectType.LECTURE,
                professor="Prof 2",
                available_slots=[
                    TimeSlot(time(9, 0), time(11, 0), DayOfWeek.MONDAY) # CONFLICTO!!!
                ]
            )
        ]

        self.constraints = StudentConstraint(
            constraint_type="test",
            description="Test constraints"
        )

    def test_optimizer_handles_conflicting_schedules(self):
        """
        Test: El optimizador debe manejar conflictos de horario correctamente
        """
        # Given: Materias con horarios conflictivos
        required_subjects = {"SUBJ1", "SUBJ2"}

        # When: Optimizar horario
        result = self.optimizer.optimize(
            self.conflicting_subjects,
            self.constraints,
            required_subjects
        )

        # Then: Debe retornar un horario válido o None si no es posible
        if result is not None:
            assert not result.has_conflicts()
        # Si es None, significa que no se pudo resolver el conflicto (comportamiento esperado)
    
    def test_optimizer_respects_early_class_constraint(self):
        """
        Test: El optimizador debe respetar la restricción de clases tempranas
        """

        # Given: Materia muy temprana y restricción de evitar clases tempranas
        early_subject = Subject(
            code="EARLY",
            name="Materia Temprana",
            credits=4,
            subject_type=SubjectType.LECTURE,
            professor="Prof Early",
            available_slots=[
                TimeSlot(time(7, 0), time(9, 0), DayOfWeek.MONDAY),
                TimeSlot(time(10, 0), time(12, 0), DayOfWeek.TUESDAY), # Alternativa
            ]
        )

        constraints_no_early = StudentConstraint(
            constraint_type="no_early",
            description="Sin clases tempranas",
            avoid_early_classes=True
        )

        # When: Optimizar con restricción
        result = self.optimizer.optimize(
            [early_subject],
            constraints_no_early,
            {"EARLY"}
        )

        # Then: Debe seleccionar el horario de las 10:00 AM
        if result is not None:
            selected_slot = result.schedule_slots[0].time_slot
            assert selected_slot.start_time >= time(9, 0)

# Fixtures para pruebas de integración
@pytest.fixture
def sample_cucei_subjects() -> List[Subject]:
    """
    Fixture que proporciona materias de ejemplo de CUCEI
    Implementa el patrón Test Data Builder
    """
    return [
        Subject(
            code="CC101",
            name="Programación I",
            credits=8,
            subject_type=SubjectType.LECTURE,
            professor="Dr. García López",
            available_slots=[
                TimeSlot(time(10, 0), time(12, 0), DayOfWeek.MONDAY), # Cambiado a 10:00 AM
                TimeSlot(time(10, 0), time(12, 0), DayOfWeek.WEDNESDAY)
            ]
        ),
        Subject(
            code="MAT101", 
            name="Cálculo Diferencial",
            credits=8,
            subject_type=SubjectType.LECTURE,
            professor="Dr. Rodríguez Pérez",
            available_slots=[
                TimeSlot(time(14, 0), time(16, 0), DayOfWeek.TUESDAY), # Cambiado para evitar conflicto
                TimeSlot(time(14, 0), time(16, 0), DayOfWeek.THURSDAY),
            ]
        ),
        Subject(
            code="LAB101",
            name="Laboratorio de Programación",
            credits=4,
            subject_type=SubjectType.LAB,
            professor="Ing. López Morales",
            available_slots=[
                TimeSlot(time(16, 0), time(18, 0), DayOfWeek.FRIDAY),  # Cambiado para evitar conflicto
            ],
            prerequisites={"CC101"}
        )
    ]

@pytest.fixture
def student_constraints() -> StudentConstraint:
    """ Fixture para restricciones estándar de estudiante """
    return StudentConstraint(
        constraint_type="standard",
        description="Restricciones estándar",
        min_break_minutes=30,
        max_daily_hours=8,
        avoid_early_classes=True,
        avoid_late_classes=False
    )

def test_integration_full_schedule_generation(sample_cucei_subjects, student_constraints):
    """
    Test de integración: Generación completa de horario
    Prueba el flujo completo del sistema
    """
    # Given: Servicio, materias y restricciones
    service = ScheduleGeneratorService()
    required_subjects = {"CC101", "MAT101", "LAB101"}

    # When: Generar horario completo
    result = service.generate_schedule(
        sample_cucei_subjects,
        student_constraints,
        required_subjects
    )

    # Then: Verificar resultado completo
    assert result is not None
    assert result.total_credits == 20 # 8 + 8 + 4
    assert len(result.schedule_slots) == 3
    assert not result.has_conflicts()

    # Verificar que se respetan las restricciones
    for slot in result.schedule_slots:
        if student_constraints.avoid_early_classes:
            assert slot.time_slot.start_time >= time(9, 0)