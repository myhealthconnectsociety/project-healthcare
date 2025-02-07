from xcov19.app.graphql.inputs import GeoLocationInput
import strawberry
from xcov19.app.graphql.schema import (
    AddressType,
    FacilitiesResultType,
    GeoLocationType,
)
from xcov19.services.diagnosis import DiagnosisQueryService
from xcov19.services.geolocation import GeolocationQueryService


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
    async def enqueue_diagnosis_query(self, query: str) -> str:
        query_id = await DiagnosisQueryService.enqueue_diagnosis_query(query)
        # TODO: log all print stmts
        print(f"query id is {query_id}")
        return query_id

    @strawberry.mutation
    async def store_query_geolocation(
        self, query_id: str, geolocation: GeoLocationInput
    ) -> None:
        lat, lng = getattr(geolocation, "lat"), getattr(geolocation, "lng")
        await GeolocationQueryService.store_location_query(
            query_id=query_id, geolocation=(lat, lng)
        )


@strawberry.type
class Query:
    # TODO:
    # 1. Implement async def get_patient
    # 2. Permissions classes
    # patient: PatientType = strawberry.field(
    #     resolver=get_patient,
    #     description="Fetch patient details."
    #     # permission_classes=
    #     )

    # TODO: Use GeolocationQueryService.fetch_facilities
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
