import pydantic as pyd


class Location(pyd.BaseModel):
    lat: float
    lng: float
    city: str
    state: str
    country: str


class RegisteringUser(pyd.BaseModel):
    name: str
    title: str
    contact_number: str
