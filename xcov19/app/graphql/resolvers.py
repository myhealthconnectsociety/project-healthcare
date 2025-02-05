from typing import List
import strawberry
from xcov19.app.graphql.schema import (
    AddressType,
    FacilitiesResultType,
    GeoLocationType,
    PatientType,
)
from xcov19.services.diagnosis import DiagnosisQueryService

# TODO: Impl DiagnoseService
# Enqueue diagnosis
# fetch splty of diagnosis via external API
# filter by splty the rows with query_id in aux table
# async save this result to diagnosis table
# return result

# TODO: Implement Geolocation application service GeoLocationService
# Service should Enqueue request, filter matching rows by geolocation,
#   store in a temp row in aux sheet/table.
# dummy impl


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def enqueue_diagnosis_query(self, query: str) -> None:
        response = DiagnosisQueryService.enqueue_diagnosis_query(query)
        # TODO: log all print stmts
        print(f"queue id is {await response}")


@strawberry.type
class Query:
    patients: List[PatientType] = strawberry.field(
        resolver=lambda: [
            PatientType(
                cust_id="SomeId",
                query="Find nearest facility. I got the moves",
                geo_location=(108, 108),
            )
        ]
    )

    # TODO: fetch_facilities_by_address
    facilities: FacilitiesResultType = strawberry.field(
        resolver=lambda: FacilitiesResultType(
            name="A place to dine",
            address=AddressType(
                name="What a place",
                street="Some nice address",
                city="VA",
                state="Lugano",
                zip="0923",
                country="IT",
            ),
            geolocation=GeoLocationType(lat=101, lng=108),
            contact="+9191919191",
            facility_type="GOOD_FACILTY",
            ownership="OWNED",
            specialties=["this", "that", "then"],
            stars=5,
            reviews=198,
            rank=1,
            estimated_time=1.08,
        )
    )
