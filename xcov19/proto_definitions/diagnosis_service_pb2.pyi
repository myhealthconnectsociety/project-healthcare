from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class DiagnosisQueryRequest(_message.Message):
    __slots__ = ("query_id", "query")
    QUERY_ID_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query_id: str
    query: str
    def __init__(
        self, query_id: _Optional[str] = ..., query: _Optional[str] = ...
    ) -> None: ...

class EmptyDiagnosisQueryResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
