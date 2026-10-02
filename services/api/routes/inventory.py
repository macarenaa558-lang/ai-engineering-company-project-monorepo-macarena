from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, func, select

from auth import get_current_user
from database import get_db
from models import Ingredient, IngredientEntry, IngredientExit
from schemas import (
    IngredientCreate,
    IngredientEntryCreate,
    IngredientEntryResponse,
    IngredientExitCreate,
    IngredientExitResponse,
    IngredientResponse,
    OrderResponse,
)


router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
)


def calculate_stock(
    db: Session,
    ingredient_id: int,
) -> float:
    inbound_statement = (
        select(
            func.coalesce(
                func.sum(IngredientEntry.quantity),
                0,
            )
        )
        .where(
            IngredientEntry.ingredient_id == ingredient_id
        )
    )

    outbound_statement = (
        select(
            func.coalesce(
                func.sum(IngredientExit.quantity),
                0,
            )
        )
        .where(
            IngredientExit.ingredient_id == ingredient_id
        )
    )

    total_in = db.exec(inbound_statement).one()
    total_out = db.exec(outbound_statement).one()

    return float(total_in) - float(total_out)


def ingredient_response(
    db: Session,
    ingredient: Ingredient,
) -> IngredientResponse:
    return IngredientResponse(
        id=ingredient.id,
        name=ingredient.name,
        sku=ingredient.sku,
        unit=ingredient.unit,
        category=ingredient.category,
        country=ingredient.country,
        current_stock=calculate_stock(
            db,
            ingredient.id,
        ),
    )


@router.get(
    "/products",
    response_model=list[IngredientResponse],
)
def get_products(
    db: Session = Depends(get_db),
):
    ingredients = db.exec(
        select(Ingredient)
    ).all()

    return [
        ingredient_response(db, ingredient)
        for ingredient in ingredients
    ]


@router.post(
    "/products",
    response_model=IngredientResponse,
    status_code=201,
)
def create_product(
    payload: IngredientCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    existing = db.exec(
        select(Ingredient).where(
            Ingredient.sku == payload.sku
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="An ingredient with this SKU already exists",
        )

    ingredient = Ingredient(
        **payload.model_dump()
    )

    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)

    return ingredient_response(db, ingredient)


@router.get(
    "/products/{product_id}",
    response_model=IngredientResponse,
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    ingredient = db.get(
        Ingredient,
        product_id,
    )

    if not ingredient:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return ingredient_response(db, ingredient)


@router.post(
    "/orders/inbound",
    response_model=IngredientEntryResponse,
    status_code=201,
)
def create_inbound_order(
    payload: IngredientEntryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    ingredient = db.get(
        Ingredient,
        payload.ingredient_id,
    )

    if not ingredient:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    order = IngredientEntry(
        **payload.model_dump(),
        user_uuid=str(current_user["id"]),
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    return IngredientEntryResponse.model_validate(
        order
    )


@router.post(
    "/orders/outbound",
    response_model=IngredientExitResponse,
    status_code=201,
)
def create_outbound_order(
    payload: IngredientExitCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    ingredient = db.get(
        Ingredient,
        payload.ingredient_id,
    )

    if not ingredient:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    available = calculate_stock(
        db,
        ingredient.id,
    )

    if payload.quantity > available:
        raise HTTPException(
            status_code=400,
            detail=(
                "Insufficient stock for ingredient "
                f"'{ingredient.name}'. Available: "
                f"{available}, requested: "
                f"{payload.quantity}."
            ),
        )

    order = IngredientExit(
        **payload.model_dump(),
        user_uuid=str(current_user["id"]),
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    return IngredientExitResponse.model_validate(
        order
    )


@router.get(
    "/orders",
    response_model=list[OrderResponse],
)
def get_orders(
    db: Session = Depends(get_db),
):
    entry_statement = (
        select(IngredientEntry, Ingredient)
        .join(
            Ingredient,
            IngredientEntry.ingredient_id
            == Ingredient.id,
        )
    )

    exit_statement = (
        select(IngredientExit, Ingredient)
        .join(
            Ingredient,
            IngredientExit.ingredient_id
            == Ingredient.id,
        )
    )

    entries = db.exec(entry_statement).all()
    exits = db.exec(exit_statement).all()

    movements = []

    for entry, ingredient in entries:
        movements.append(
            {
                "id": entry.id,
                "movement_type": "inbound",
                "quantity": entry.quantity,
                "created_at": entry.created_at,
                "user_uuid": entry.user_uuid,
                "ingredient": {
                    "id": ingredient.id,
                    "name": ingredient.name,
                    "sku": ingredient.sku,
                    "unit": ingredient.unit,
                    "category": ingredient.category,
                    "country": ingredient.country,
                },
            }
        )

    for exit_order, ingredient in exits:
        movements.append(
            {
                "id": exit_order.id,
                "movement_type": "outbound",
                "quantity": exit_order.quantity,
                "created_at": exit_order.created_at,
                "user_uuid": exit_order.user_uuid,
                "ingredient": {
                    "id": ingredient.id,
                    "name": ingredient.name,
                    "sku": ingredient.sku,
                    "unit": ingredient.unit,
                    "category": ingredient.category,
                    "country": ingredient.country,
                },
            }
        )

    movements.sort(
        key=lambda movement: movement["created_at"]
    )

    return movements