from xcov19.services.queue import diagnosis_queue


class DiagnosisQueryService:
    """
    The DiagnosisQueryService class is responsible for
    handling diagnosis queries within the GraphQL-driven backend.

    It interacts with the GraphQL resolvers to
    process diagnosis-related requests. This service may include methods to
    initiate diagnosis queries, retrieve diagnosis results,
    and perform queuing and processing workflows.
    """

    # TODO: convert print to log and plug to logging backend
    @classmethod
    async def enqueue_diagnosis_query(cls, query: str) -> str:
        try:
            return await diagnosis_queue.enqueue(query)
        except (BufferError, OverflowError) as e:
            print("queue error")
            raise (e)
