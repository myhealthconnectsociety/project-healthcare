"""Controller API routes for case diagnosis."""

import logging
from blacksheep import Response, FromJSON, json
from blacksheep.server.controllers import APIController
from xcov19.app.controllers import post

from xcov19.dto import DiagnosisQueryJSON
from xcov19.app.settings import FromOriginMatchHeader

# Set up logging configuration (adjust as needed)
logging.basicConfig(level=logging.DEBUG)

class DiagnosisController(APIController):
    @classmethod
    def route(cls) -> str | None:
        return "diagnose"

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

        # Replace print statements with logging
        logging.debug("%s", diagnosis_query.value)
        logging.debug("DiagnosisController invoked with data: %s", diagnosis_query.value)
        
        return json({"response": "ok"})
