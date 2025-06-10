from dataclasses import dataclass

from typing import TypeAlias
from xcov19.domain.models import GeoLocation

CustomerId: TypeAlias = str

# domain entities


@dataclass
class Patient:
    cust_id: CustomerId
    query: str
    geo_location: GeoLocation
