import pydantic as pyd


class Location(pyd.BaseModel):
    lat: float
    lng: float
    city: str
    state: str
    country: str


class LocationRecord(Location):
    """Orm mappable Location record that fetches from database."""

    id: int

    class Config:
        orm_mode = True


class RegisteringUser(pyd.BaseModel):
    name: str
    title: str
    contact_number: str


class ClericalRegisteredRecord(RegisteringUser):
    """Orm mappable Clerical Registration record that fetches from database."""

    id: int

    class Config:
        orm_mode = True
