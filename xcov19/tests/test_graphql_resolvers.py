import pytest
from unittest.mock import AsyncMock, patch
from starlette.testclient import TestClient
from strawberry.asgi.test import GraphQLTestClient

from xcov19.app.graphql.main import app


@pytest.fixture(scope="module")
def gql_client():
    return GraphQLTestClient(TestClient(app))


def test_enqueue_diagnosis_query(gql_client):
    mutation = """
    mutation($query: String!) {
        enqueueDiagnosisQuery(query: $query)
    }
    """
    with patch(
        "xcov19.app.graphql.resolvers.enqueue_diagnosis",
        new_callable=AsyncMock,
    ) as mock_enqueue:
        mock_enqueue.return_value = "dummy-id"
        result = gql_client.query(mutation, variables={"query": "test"})
        assert result.data == {"enqueueDiagnosisQuery": "dummy-id"}
        mock_enqueue.assert_awaited_once_with("test")


def test_store_query_geolocation(gql_client):
    mutation = """
    mutation($id: String!, $geo: GeoLocationInput!) {
        storeQueryGeolocation(queryId: $id, geolocation: $geo)
    }
    """
    with patch(
        "xcov19.app.graphql.resolvers.GeolocationQueryService.store_location_query",
        new_callable=AsyncMock,
    ) as mock_store:
        mock_store.return_value = None
        variables = {"id": "qid", "geo": {"lat": 1.0, "lng": 2.0}}
        result = gql_client.query(mutation, variables=variables)
        assert result.data == {"storeQueryGeolocation": None}
        mock_store.assert_awaited_once_with(query_id="qid", geolocation=(1.0, 2.0))


def test_facilities_query_returns_mocked_structure(gql_client):
    query = """
    query {
        facilities {
            name
            address { name street city state zip country }
            geolocation { lat lng }
            contact
            facilityType
            ownership
            specialties
            stars
            reviews
            rank
            estimatedTime
        }
    }
    """
    result = gql_client.query(query)
    assert result.data == {
        "facilities": {
            "name": "A place to dine",
            "address": {
                "name": "What a place",
                "street": "Some nice address",
                "city": "VA",
                "state": "Lugano",
                "zip": "0923",
                "country": "IT",
            },
            "geolocation": {"lat": 101.0, "lng": 108.0},
            "contact": "+9191919191",
            "facilityType": "GOOD_FACILTY",
            "ownership": "OWNED",
            "specialties": ["this", "that", "then"],
            "stars": 5,
            "reviews": 198,
            "rank": 1,
            "estimatedTime": 1.08,
        }
    }
