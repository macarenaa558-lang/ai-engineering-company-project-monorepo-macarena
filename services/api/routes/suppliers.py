from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from tinydb import Query

from auth import get_current_user
from database import suppliers_table
from models import (
    SupplierCreate,
    SupplierRateUpdate,
    SupplierResponse,
    SupplierStatusUpdate,
)


router = APIRouter(
    prefix="/suppliers",
    tags=["suppliers"],
)

Supplier = Query()


def supplier_with_id(document):
    supplier = dict(document)
    supplier["id"] = document.doc_id
    return supplier


@router.post("", response_model=SupplierResponse)
def create_supplier(
    data: SupplierCreate,
    current_user: dict = Depends(get_current_user),
):
    supplier_data = data.model_dump()
    supplier_data["status"] = data.status.value
    supplier_data["updated_at"] = datetime.now(
        timezone.utc
    ).isoformat()

    document_id = suppliers_table.insert(
        supplier_data
    )

    supplier_data["id"] = document_id

    return supplier_data


@router.get("", response_model=list[SupplierResponse])
def list_suppliers(
    country: Optional[str] = None,
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    suppliers = suppliers_table.all()

    if country:
        suppliers = [
            supplier
            for supplier in suppliers
            if supplier.get("country") == country
        ]

    if category:
        suppliers = [
            supplier
            for supplier in suppliers
            if category in supplier.get("categories", [])
        ]

    return [
        supplier_with_id(supplier)
        for supplier in suppliers
    ]


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(
    supplier_id: int,
    current_user: dict = Depends(get_current_user),
):
    supplier = suppliers_table.get(
        doc_id=supplier_id
    )

    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Proveedor no encontrado",
        )

    return supplier_with_id(supplier)


@router.patch("/{supplier_id}/rate", response_model=SupplierResponse)
def update_supplier_rate(
    supplier_id: int,
    data: SupplierRateUpdate,
    current_user: dict = Depends(get_current_user),
):
    supplier = suppliers_table.get(
        doc_id=supplier_id
    )

    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Proveedor no encontrado",
        )

    suppliers_table.update(
        {
            "rate_per_unit": data.rate_per_unit,
            "updated_at": datetime.now(
                timezone.utc
            ).isoformat(),
        },
        doc_ids=[supplier_id],
    )

    updated_supplier = suppliers_table.get(
        doc_id=supplier_id
    )

    return supplier_with_id(updated_supplier)


@router.patch("/{supplier_id}/status", response_model=SupplierResponse)
def update_supplier_status(
    supplier_id: int,
    data: SupplierStatusUpdate,
    current_user: dict = Depends(get_current_user),
):
    supplier = suppliers_table.get(
        doc_id=supplier_id
    )

    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Proveedor no encontrado",
        )

    suppliers_table.update(
        {
            "status": data.status.value
        },
        doc_ids=[supplier_id],
    )

    updated_supplier = suppliers_table.get(
        doc_id=supplier_id
    )

    return supplier_with_id(updated_supplier)


@router.delete("/{supplier_id}")
def delete_supplier(
    supplier_id: int,
    current_user: dict = Depends(get_current_user),
):
    supplier = suppliers_table.get(
        doc_id=supplier_id
    )

    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Proveedor no encontrado",
        )

    suppliers_table.remove(
        doc_ids=[supplier_id]
    )

    return {
        "message": "Proveedor eliminado"
    }