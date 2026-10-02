from datetime import datetime, timezone
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from tinydb import Query
from sqlmodel import Session, SQLModel, select

from database import engine, suppliers_table
from models import Ingredient, IngredientEntry, IngredientExit


Supplier = Query()
USER_UUID = "8d0dbf3c-7284-4c57-9578-c31868dde75c"


SUPPLIERS_SEED = [
    {
        "name": "Carnes del Valle S.A.S.",
        "country": "Colombia",
        "categories": ["carne"],
        "rate_per_unit": 28500.0,
        "currency": "COP",
        "status": "active",
        "contact_email": "ventas@carnesdelvalle.co",
        "notes": "Proveedor principal de res y cerdo para Medellín. Entrega martes y viernes."
    },
    {
        "name": "Frigorífico Antioqueño",
        "country": "Colombia",
        "categories": ["carne"],
        "rate_per_unit": 27900.0,
        "currency": "COP",
        "status": "active",
        "contact_email": "pedidos@frigorificoa.co",
        "notes": "Proveedor secundario. Usado cuando Carnes del Valle no tiene stock."
    },
    {
        "name": "Verduras La Cosecha",
        "country": "Colombia",
        "categories": ["verduras_y_hortalizas"],
        "rate_per_unit": 3200.0,
        "currency": "COP",
        "status": "active",
        "contact_email": "lacosecha@gmail.com",
        "notes": "Mercado mayorista de Medellín. Entrega diaria antes de las 7am."
    },
    {
        "name": "Condimentos El Sabor",
        "country": "Colombia",
        "categories": ["salsas_y_condimentos"],
        "rate_per_unit": 12400.0,
        "currency": "COP",
        "status": "active",
        "contact_email": "info@elsabor.co"
    },
    {
        "name": "Distribuidora RefriCol",
        "country": "Colombia",
        "categories": ["bebidas", "lacteos"],
        "rate_per_unit": 4100.0,
        "currency": "COP",
        "status": "active",
        "contact_email": "refricol.pedidos@gmail.com"
    },
    {
        "name": "Empaques y Más",
        "country": "Colombia",
        "categories": ["packaging"],
        "rate_per_unit": 890.0,
        "currency": "COP",
        "status": "active",
        "contact_email": "ventas@empaquesymas.co",
        "notes": "Suministra cajas, bolsas y servilletas para todos los locales de Colombia."
    },
    {
        "name": "Limpiahogar Profesional",
        "country": "Colombia",
        "categories": ["productos_limpieza"],
        "rate_per_unit": 7600.0,
        "currency": "COP",
        "status": "suspended",
        "contact_email": "limpiahogar@promail.co",
        "notes": "Suspendido por incumplimiento en entregas. En revisión por Lucía."
    },
    {
        "name": "CarboCo",
        "country": "Colombia",
        "categories": ["carbon_y_combustible"],
        "rate_per_unit": 45000.0,
        "currency": "COP",
        "status": "active",
        "contact_email": "pedidos@carboco.co",
        "notes": "Único proveedor homologado de carbón para las brasas. Contrato anual."
    },
    {
        "name": "Miami Meat Distributors LLC",
        "country": "USA",
        "categories": ["carne"],
        "rate_per_unit": 6.80,
        "currency": "USD",
        "status": "active",
        "contact_email": "orders@miamimeat.com",
        "notes": "Proveedor principal de carne para los locales de Florida."
    },
    {
        "name": "Sunshine Produce FL",
        "country": "USA",
        "categories": ["verduras_y_hortalizas"],
        "rate_per_unit": 2.15,
        "currency": "USD",
        "status": "active",
        "contact_email": "sales@sunshineproduce.com"
    },
    {
        "name": "Latin Flavors Inc.",
        "country": "USA",
        "categories": ["salsas_y_condimentos", "bebidas"],
        "rate_per_unit": 4.50,
        "currency": "USD",
        "status": "active",
        "contact_email": "orders@latinflavors.com",
        "notes": "Importa salsas colombianas para el mercado de Florida."
    },
    {
        "name": "PackRight USA",
        "country": "USA",
        "categories": ["packaging"],
        "rate_per_unit": 0.35,
        "currency": "USD",
        "status": "active",
        "contact_email": "info@packright.us"
    },
    {
        "name": "CleanPro Florida",
        "country": "USA",
        "categories": ["productos_limpieza"],
        "rate_per_unit": 12.90,
        "currency": "USD",
        "status": "active",
        "contact_email": "orders@cleanproflorida.com"
    },
    {
        "name": "GrillFuel Supply Co.",
        "country": "USA",
        "categories": ["carbon_y_combustible"],
        "rate_per_unit": 38.50,
        "currency": "USD",
        "status": "active",
        "contact_email": "supply@grillfuel.com",
        "notes": "Proveedor de carbón para Florida. Precio sujeto a revisión trimestral."
    },
    {
        "name": "Bebidas Andinas",
        "country": "Colombia",
        "categories": ["bebidas"],
        "rate_per_unit": 3800.0,
        "currency": "COP",
        "status": "suspended",
        "contact_email": "ventas@bebidasandinas.co",
        "notes": "Suspendido. Precio por encima del mercado tras última renegociación."
    }
]


def seed_suppliers():
    inserted = 0

    for supplier in SUPPLIERS_SEED:
        exists = suppliers_table.get(
            Supplier.name == supplier["name"]
        )

        if exists:
            continue

        supplier_data = supplier.copy()
        supplier_data["updated_at"] = datetime.now(
            timezone.utc
        ).isoformat()

        suppliers_table.insert(supplier_data)
        inserted += 1

    print(f"Proveedores insertados: {inserted}")

def seed_inventory():
    SQLModel.metadata.create_all(engine)

    with Session(engine) as db:
        existing = db.exec(
            select(Ingredient)
        ).first()

        if existing:
            print(
                "Ya hay ingredientes cargados. "
                "No se ejecutó el seed de inventario."
            )
            return

        ingredients = [
            Ingredient(
                name="Falda de ternera",
                sku="BRS-BEEF-001",
                unit="kg",
                category="meat",
                country="CO",
            ),
            Ingredient(
                name="Costilla de cerdo",
                sku="BRS-PORK-001",
                unit="kg",
                category="meat",
                country="US",
            ),
            Ingredient(
                name="Chimichurri",
                sku="BRS-SAUCE-001",
                unit="litro",
                category="sauce",
                country="CO",
            ),
            Ingredient(
                name="Salsa BBQ de la casa",
                sku="BRS-SAUCE-002",
                unit="litro",
                category="sauce",
                country="US",
            ),
            Ingredient(
                name="Yuca",
                sku="BRS-PROD-001",
                unit="kg",
                category="produce",
                country="CO",
            ),
            Ingredient(
                name="Caja para llevar (M)",
                sku="BRS-PKG-001",
                unit="unidad",
                category="packaging",
                country="CO",
            ),
        ]

        db.add_all(ingredients)
        db.commit()

        for ingredient in ingredients:
            db.refresh(ingredient)

        by_sku = {
            ingredient.sku: ingredient
            for ingredient in ingredients
        }

        entries = [
            IngredientEntry(
                ingredient_id=by_sku["BRS-BEEF-001"].id,
                quantity=50,
                supplier_name="Carnes del Valle S.A.",
                location_id=1,
                user_uuid=USER_UUID,
            ),
            IngredientEntry(
                ingredient_id=by_sku["BRS-BEEF-001"].id,
                quantity=30,
                supplier_name="Carnes del Valle S.A.",
                location_id=1,
                user_uuid=USER_UUID,
            ),
            IngredientEntry(
                ingredient_id=by_sku["BRS-PORK-001"].id,
                quantity=40,
                supplier_name="MiamiMeat Co.",
                location_id=2,
                user_uuid=USER_UUID,
            ),
            IngredientEntry(
                ingredient_id=by_sku["BRS-SAUCE-001"].id,
                quantity=20,
                supplier_name="Salsas Artesanales Ltda.",
                location_id=3,
                user_uuid=USER_UUID,
            ),
        ]

        db.add_all(entries)
        db.commit()

        exits = [
            IngredientExit(
                ingredient_id=by_sku["BRS-BEEF-001"].id,
                quantity=10,
                reason="consumption",
                location_id=1,
                user_uuid=USER_UUID,
            ),
            IngredientExit(
                ingredient_id=by_sku["BRS-BEEF-001"].id,
                quantity=5,
                reason="waste",
                location_id=1,
                user_uuid=USER_UUID,
            ),
            IngredientExit(
                ingredient_id=by_sku["BRS-PORK-001"].id,
                quantity=8,
                reason="consumption",
                location_id=2,
                user_uuid=USER_UUID,
            ),
        ]

        db.add_all(exits)
        db.commit()

        print("Seed de inventario de Brasaland cargado correctamente.")

def main():
    seed_suppliers()
    seed_inventory()


if __name__ == "__main__":
    main()