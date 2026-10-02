import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  createOutboundOrder,
  listProducts,
} from "../../services/inventory";
import type { Ingredient } from "../../types/inventory";

export default function InventoryOutbound() {
  const [searchParams] = useSearchParams();

  const [products, setProducts] = useState<Ingredient[]>([]);
  const [ingredientId, setIngredientId] = useState("");
  const [quantity, setQuantity] = useState("");
  const [reason, setReason] = useState<
    "consumption" | "waste"
  >("consumption");
  const [locationId, setLocationId] = useState("");

  const [loadingProducts, setLoadingProducts] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [quantityError, setQuantityError] = useState("");
  const [success, setSuccess] = useState("");

  const selectedProduct = products.find(
    (product) => product.id === Number(ingredientId),
  );

  const requestedQuantity = Number(quantity);

  const exceedsStock =
    Boolean(selectedProduct) &&
    quantity !== "" &&
    Number.isFinite(requestedQuantity) &&
    requestedQuantity > (selectedProduct?.current_stock ?? 0);

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
    setQuantityError("");
    setSuccess("");

    const parsedIngredientId = Number(ingredientId);
    const parsedQuantity = Number(quantity);
    const parsedLocationId = Number(locationId);

    if (!parsedIngredientId) {
      setError("Seleccioná un ingrediente.");
      return;
    }

    if (!Number.isFinite(parsedQuantity) || parsedQuantity <= 0) {
      setQuantityError("La cantidad debe ser mayor a 0.");
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
      await createOutboundOrder({
        ingredient_id: parsedIngredientId,
        quantity: parsedQuantity,
        reason,
        location_id: parsedLocationId,
      });

      setSuccess("Salida de inventario registrada correctamente.");

      // Actualizamos la lista para obtener el nuevo current_stock
      // calculado por el backend.
      const updatedProducts = await listProducts();
      setProducts(updatedProducts);

      setIngredientId("");
      setQuantity("");
      setReason("consumption");
      setLocationId("");
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "No se pudo registrar la salida.";

      // El backend es la fuente de verdad para validar el stock.
      // Su error 400 de stock insuficiente se muestra junto
      // al campo cantidad.
      if (
        message.toLowerCase().includes("insufficient stock")
      ) {
        setQuantityError(message);
      } else {
        setError(message);
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="inventory-page">
      <div className="inventory-header">
        <div>
          <span className="eyebrow">INVENTARIO</span>
          <h1>Nueva salida</h1>
          <p>
            Registrá el consumo o desperdicio de ingredientes de
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
            onChange={(event) => {
              setIngredientId(event.target.value);
              setQuantityError("");
            }}
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

        {selectedProduct && (
          <div className="inventory-stock-info">
            <strong>Stock actual:</strong>{" "}
            {selectedProduct.current_stock}{" "}
            {selectedProduct.unit}
          </div>
        )}

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
            onChange={(event) => {
              setQuantity(event.target.value);
              setQuantityError("");
            }}
            placeholder="Ej.: 5.5"
            disabled={submitting}
          />

          {exceedsStock && (
            <div className="inventory-warning">
              La cantidad solicitada supera el stock actual de{" "}
              {selectedProduct?.current_stock}{" "}
              {selectedProduct?.unit}. El servidor validará el
              stock al registrar la salida.
            </div>
          )}

          {quantityError && (
            <div className="error-message">
              {quantityError}
            </div>
          )}
        </div>

        <div className="inventory-form-group">
          <label htmlFor="reason">
            Motivo
          </label>

          <select
            id="reason"
            value={reason}
            onChange={(event) =>
              setReason(
                event.target.value as
                  | "consumption"
                  | "waste",
              )
            }
            disabled={submitting}
          >
            <option value="consumption">
              Consumo
            </option>

            <option value="waste">
              Desperdicio
            </option>
          </select>
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
            : "Registrar salida"}
        </button>
      </form>
    </div>
  );
}