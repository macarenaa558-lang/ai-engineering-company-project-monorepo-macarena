import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  createInboundOrder,
  listProducts,
} from "../../services/inventory";
import type { Ingredient } from "../../types/inventory";
import BackofficeLink from "../../components/inventory/BackofficeLink";

export default function InventoryInbound() {
  const [searchParams] = useSearchParams();

  const [products, setProducts] = useState<Ingredient[]>([]);
  const [ingredientId, setIngredientId] = useState("");
  const [quantity, setQuantity] = useState("");
  const [supplierName, setSupplierName] = useState("");
  const [locationId, setLocationId] = useState("");

  const [loadingProducts, setLoadingProducts] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    const loadProducts = async () => {
      setLoadingProducts(true);
      setError("");

      try {
        const data = await listProducts();
        setProducts(data);

        const productId = searchParams.get("productId");

        if (
          productId &&
          data.some(
            (product) => product.id === Number(productId),
          )
        ) {
          setIngredientId(productId);
        }
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "No se pudieron cargar los ingredientes.",
        );
      } finally {
        setLoadingProducts(false);
      }
    };

    loadProducts();
  }, [searchParams]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();

    setError("");
    setSuccess("");

    const parsedIngredientId = Number(ingredientId);
    const parsedQuantity = Number(quantity);
    const parsedLocationId = Number(locationId);

    if (!parsedIngredientId) {
      setError("Seleccioná un ingrediente.");
      return;
    }

    if (!Number.isFinite(parsedQuantity) || parsedQuantity <= 0) {
      setError("La cantidad debe ser mayor a 0.");
      return;
    }

    if (!supplierName.trim()) {
      setError("Ingresá el nombre del proveedor.");
      return;
    }

    if (
      !Number.isInteger(parsedLocationId) ||
      parsedLocationId < 1 ||
      parsedLocationId > 14
    ) {
      setError("El local debe estar entre 1 y 14.");
      return;
    }

    setSubmitting(true);

    try {
      await createInboundOrder({
        ingredient_id: parsedIngredientId,
        quantity: parsedQuantity,
        supplier_name: supplierName.trim(),
        location_id: parsedLocationId,
      });

      setSuccess("Entrada de inventario registrada correctamente.");

      setIngredientId("");
      setQuantity("");
      setSupplierName("");
      setLocationId("");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "No se pudo registrar la entrada.",
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="inventory-page">
      <BackofficeLink />
      <div className="inventory-header">
        <div>
          <span className="eyebrow">INVENTARIO</span>
          <h1>Nueva entrada</h1>
          <p>
            Registrá el ingreso de ingredientes al inventario de
            Brasaland.
          </p>
        </div>
      </div>

      <nav className="inventory-nav">
        <Link to="/backoffice/inventory/products">
          Ingredientes
        </Link>

        <Link to="/backoffice/inventory/orders/inbound">
          Nueva entrada
        </Link>

        <Link to="/backoffice/inventory/orders/outbound">
          Nueva salida
        </Link>

        <Link to="/backoffice/inventory/orders">
          Historial
        </Link>
      </nav>

      <form
        className="inventory-form"
        onSubmit={handleSubmit}
      >
        <div className="inventory-form-group">
          <label htmlFor="ingredient">
            Ingrediente
          </label>

          <select
            id="ingredient"
            value={ingredientId}
            onChange={(event) =>
              setIngredientId(event.target.value)
            }
            disabled={loadingProducts || submitting}
          >
            <option value="">
              {loadingProducts
                ? "Cargando ingredientes..."
                : "Seleccioná un ingrediente"}
            </option>

            {products.map((product) => (
              <option
                key={product.id}
                value={product.id}
              >
                {product.name} — {product.sku}
              </option>
            ))}
          </select>
        </div>

        <div className="inventory-form-group">
          <label htmlFor="quantity">
            Cantidad
          </label>

          <input
            id="quantity"
            type="number"
            min="0.01"
            step="0.01"
            value={quantity}
            onChange={(event) =>
              setQuantity(event.target.value)
            }
            placeholder="Ej.: 10.5"
            disabled={submitting}
          />
        </div>

        <div className="inventory-form-group">
          <label htmlFor="supplier">
            Proveedor
          </label>

          <input
            id="supplier"
            type="text"
            value={supplierName}
            onChange={(event) =>
              setSupplierName(event.target.value)
            }
            placeholder="Nombre del proveedor"
            disabled={submitting}
          />
        </div>

        <div className="inventory-form-group">
          <label htmlFor="location">
            Local
          </label>

          <select
            id="location"
            value={locationId}
            onChange={(event) =>
              setLocationId(event.target.value)
            }
            disabled={submitting}
          >
            <option value="">
              Seleccioná un local
            </option>

            {Array.from(
              { length: 14 },
              (_, index) => index + 1,
            ).map((location) => (
              <option
                key={location}
                value={location}
              >
                Local {location}
              </option>
            ))}
          </select>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {success && (
          <div className="success-message">
            {success}
          </div>
        )}

        <button
          type="submit"
          className="inventory-submit"
          disabled={submitting || loadingProducts}
        >
          {submitting
            ? "Registrando..."
            : "Registrar entrada"}
        </button>
      </form>
    </div>
  );
}