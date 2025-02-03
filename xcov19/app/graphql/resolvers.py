from typing import List
import strawberry
from xcov19.app.graphql.schema import (
    AddressType,
    DiagnosisQueryType,
    FacilitiesResultType,
    GeoLocationType,
    PatientType,
    QueryIDType,
)
from strawberry.asgi import GraphQL


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

    diagnosis: DiagnosisQueryType = strawberry.field(
        resolver=lambda: DiagnosisQueryType(
            query="What is the reason for gravity i feel.",
            query_id=QueryIDType(query_id="somethignASCII"),
        )
    )

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


schema = strawberry.Schema(query=Query)

gql_app = GraphQL(schema, graphiql=True)
