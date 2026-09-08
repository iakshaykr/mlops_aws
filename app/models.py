from pydantic import BaseModel


class PredictionRequest(BaseModel):

    city: str

    area: float

    bedrooms: int

    bathrooms: int

    house_age: int

    parking: bool
