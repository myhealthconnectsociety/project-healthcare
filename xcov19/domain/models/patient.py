from typing import Annotated
import dataclasses
from dataclasses import dataclass
from xcov19.domain.models import GeoLocation

CustomerId = str

# domain entities


@dataclass
class Patient:
    cust_id: CustomerId
    query: str
    geo_location: Annotated[GeoLocation, dataclasses.field(default=(0.0, 0.0))]
