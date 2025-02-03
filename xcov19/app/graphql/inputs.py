import strawberry
from xcov19.domain.models.patient import Patient


@strawberry.input
class PatientInput(Patient):
    pass
