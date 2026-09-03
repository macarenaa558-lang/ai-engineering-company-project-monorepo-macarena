from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


VALID_CATEGORIES = [
    "carne",
    "verduras_y_hortalizas",
    "salsas_y_condimentos",
    "bebidas",
    "packaging",
    "productos_limpieza",
    "lacteos",
    "carbon_y_combustible",
]


class SupplierStatus(str, Enum):
    active = "active"
    suspended = "suspended"


class SupplierBase(BaseModel):
    name: str
    country: str
    categories: list[str] = Field(min_length=1)
    rate_per_unit: float = Field(gt=0)
    currency: str
    status: SupplierStatus
    contact_email: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("categories")
    @classmethod
    def validate_categories(cls, categories):
        invalid_categories = [
            category
            for category in categories
            if category not in VALID_CATEGORIES
        ]

        if invalid_categories:
            raise ValueError(
                f"Categorías inválidas: {invalid_categories}"
            )

        return categories

    @model_validator(mode="after")
    def validate_country_and_currency(self):
        if self.country == "Colombia" and self.currency != "COP":
            raise ValueError(
                'Los proveedores de Colombia deben usar currency="COP"'
            )

        if self.country == "USA" and self.currency != "USD":
            raise ValueError(
                'Los proveedores de USA deben usar currency="USD"'
            )

        if self.country not in ["Colombia", "USA"]:
            raise ValueError(
                'country debe ser "Colombia" o "USA"'
            )

        return self


class SupplierCreate(SupplierBase):
    pass


class SupplierResponse(SupplierBase):
    id: int
    updated_at: datetime


class SupplierRateUpdate(BaseModel):
    rate_per_unit: float = Field(gt=0)


class SupplierStatusUpdate(BaseModel):
    status: SupplierStatus