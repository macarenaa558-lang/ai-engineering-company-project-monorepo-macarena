from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from packages.shared.incidents import (
    VALID_BRANCHES as INCIDENT_BRANCHES,
    VALID_CATEGORIES as INCIDENT_CATEGORIES,
    VALID_ORIGINS as INCIDENT_ORIGINS,
    VALID_STATUSES as INCIDENT_STATUSES,
    validate_branch,
    validate_category,
    validate_origin,
    validate_status,
)


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


IncidentStatus = Enum(
    "IncidentStatus",
    {value: value for value in INCIDENT_STATUSES},
    type=str,
)

IncidentOrigin = Enum(
    "IncidentOrigin",
    {value: value for value in INCIDENT_ORIGINS},
    type=str,
)

IncidentCategory = Enum(
    "IncidentCategory",
    {value: value for value in INCIDENT_CATEGORIES},
    type=str,
)

IncidentBranch = Enum(
    "IncidentBranch",
    {value: value for value in INCIDENT_BRANCHES},
    type=str,
)


class IncidentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1)
    category: IncidentCategory
    status: IncidentStatus = IncidentStatus.open
    origin: IncidentOrigin
    branch: IncidentBranch

    @field_validator("title", "description")
    @classmethod
    def validate_not_blank(cls, value):
        if not value.strip():
            raise ValueError("Este campo no puede estar vacío")

        return value.strip()

    @model_validator(mode="after")
    def validate_incident_values(self):
        validate_status(self.status.value)
        validate_category(self.category.value)
        validate_origin(self.origin.value)
        validate_branch(self.branch.value)

        return self


class IncidentResponse(IncidentCreate):
    id: int
    created_at: datetime
    updated_at: datetime


class IncidentStatusUpdate(BaseModel):
    status: IncidentStatus

    @model_validator(mode="after")
    def validate_incident_status(self):
        validate_status(self.status.value)
        return self