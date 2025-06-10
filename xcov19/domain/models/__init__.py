from typing import Tuple, TypeAlias

Mobile: TypeAlias = str
Telephone: TypeAlias = str
MobileTelephone: TypeAlias = Mobile | Telephone
longitude: TypeAlias = float
latitude: TypeAlias = float
GeoLocation: TypeAlias = Tuple[latitude, longitude]
