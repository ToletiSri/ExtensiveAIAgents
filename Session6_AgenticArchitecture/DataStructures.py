from pydantic import BaseModel
from typing import List

# Input/Output models for tools

class CuisinePreference(BaseModel):
    cuisine: str
    is_vegetarian: bool

class SuggestedDish(BaseModel):
    dish: str

class UserOrder(BaseModel):
    mood: str
    time: str
    action: str

class WeatherInputs(BaseModel):
    place: str

class WeatherDetails(BaseModel):
    weather: str
    description: str
