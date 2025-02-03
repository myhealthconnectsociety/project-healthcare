from xcov19.app.dto import (
    Address,
    DiagnosisQueryJSON,
    FacilitiesResult,
    GeoLocation,
    QueryId,
)
from strawberry.experimental.pydantic import type as pydantic_type
import strawberry
from xcov19.domain.models.patient import Patient


# TODO: Implement FacilitiesResult; Example reference. remove later:
@strawberry.type
class PatientType(Patient): ...


@pydantic_type(model=GeoLocation, all_fields=True)
class GeoLocationType: ...


@pydantic_type(model=Address, all_fields=True)
class AddressType: ...


@pydantic_type(model=QueryId)
class QueryIDType:
    query_id: strawberry.auto


@pydantic_type(model=DiagnosisQueryJSON, all_fields=True)
class DiagnosisQueryType:
    query_id: QueryIDType


@pydantic_type(model=FacilitiesResult, all_fields=True)
class FacilitiesResultType:
    address: AddressType
    geolocation: GeoLocationType
