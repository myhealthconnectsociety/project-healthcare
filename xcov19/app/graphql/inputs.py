from xcov19.app.dto import GeoLocation
import strawberry
from strawberry.experimental import pydantic
from xcov19.domain.models.patient import Patient


@strawberry.input
class PatientInput(Patient):
    pass


@pydantic.input(model=GeoLocation, all_fields=True, use_pydantic_alias=True)
class GeoLocationInput: ...
