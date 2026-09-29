from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


IngredientCategory = Literal[
    "meat",
    "produce",
    "sauce",
    "beverage",
    "packaging",
    "cleaning",
]

IngredientCountry = Literal["CO", "US"]
IngredientUnit = Literal["kg", "litro", "unidad"]
ExitReason = Literal["consumption", "waste"]


class IngredientCreate(BaseModel):
    name: str = Field(min_length=1)
    sku: str = Field(min_length=1)
    unit: IngredientUnit
    category: IngredientCategory
    country: IngredientCountry


class IngredientResponse(IngredientCreate):
    id: int
    current_stock: float

    model_config = ConfigDict(from_attributes=True)


class IngredientEntryCreate(BaseModel):
    ingredient_id: int
    quantity: float = Field(gt=0)
    supplier_name: str = Field(min_length=1)
    location_id: int = Field(ge=1, le=14)


class IngredientExitCreate(BaseModel):
    ingredient_id: int
    quantity: float = Field(gt=0)
    reason: ExitReason
    location_id: int = Field(ge=1, le=14)


class IngredientEntryResponse(IngredientEntryCreate):
    id: int
    created_at: datetime
    user_uuid: str

    model_config = ConfigDict(from_attributes=True)


class IngredientExitResponse(IngredientExitCreate):
    id: int
    created_at: datetime
    user_uuid: str

    model_config = ConfigDict(from_attributes=True)


class OrderIngredientResponse(BaseModel):
    id: int
    name: str
    sku: str
    unit: str
    category: str
    country: str

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    movement_type: Literal["inbound", "outbound"]
    quantity: float
    created_at: datetime
    user_uuid: str
    ingredient: OrderIngredientResponse