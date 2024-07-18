"""Controller API routes for case diagnosis."""

from blacksheep import Response, FromJSON, json
from blacksheep.server.controllers import APIController, post

from xcov19.app.dto import DiagnosisQueryJSON, FromOriginMatchHeader


class DiagnosisController(APIController):
    @classmethod
    def route(cls) -> str | None:
        return "api/diagnose"

    @classmethod
    def version(cls) -> str:
        return "v1"

    @post()
    async def diagnose(
        self,
        diagnosis_query: FromJSON[DiagnosisQueryJSON],
        _from_origin_header: FromOriginMatchHeader,
    ) -> Response:
        # TODO: Impl DiagnoseService
        # Enqueue diagnosis
        # fetch splty of diagnosis via external API
        # filter by splty the rows with query_id in aux table
        # async save this result to diagnosis table
        # return result
        print(diagnosis_query.value)
        return json({"response": "ok"})
