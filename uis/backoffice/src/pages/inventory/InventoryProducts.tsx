import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listProducts } from "../../services/inventory";
import type { Ingredient } from "../../types/inventory";

// Umbrales visuales del backoffice.
// <= 5: stock bajo | <= 15: atención | > 15: saludable.
// Son indicadores visuales, no reglas de negocio del backend.
function getStockStatus(stock: number) {
  if (stock <= 5) {
    return {
      label: "Bajo",
      className: "inventory-stock inventory-stock-low",
    };
  }

  if (stock <= 15) {
    return {
      label: "Atención",
      className: "inventory-stock inventory-stock-warning",
    };
  }

  return {
    label: "Saludable",
    className: "inventory-stock inventory-stock-healthy",
  };
}

export default function InventoryProducts() {
  const [products, setProducts] = useState<Ingredient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    const loadProducts = async () => {
      setLoading(true);
      setError("");

      try {
        const data = await listProducts();

        if (active) {
          setProducts(data);
        }
      } catch (err) {
        if (active) {
          setError(
            err instanceof Error
              ? err.message
              : "No se pudo cargar el inventario.",
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    loadProducts();

    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="inventory-page">
      <div className="inventory-header">
        <div>
          <span className="eyebrow">INVENTARIO</span>
          <h1>Ingredientes</h1>
          <p>Stock actual de ingredientes de Brasaland.</p>
        </div>

        <Link
          className="inventory-history-link"
          to="/backoffice/inventory/orders"
        >
          Ver historial
        </Link>
      </div>

      <nav className="inventory-nav">
        <Link to="/backoffice/inventory/products">Ingredientes</Link>
        <Link to="/backoffice/inventory/orders/inbound">
          Nueva entrada
        </Link>
        <Link to="/backoffice/inventory/orders/outbound">
          Nueva salida
        </Link>
        <Link to="/backoffice/inventory/orders">Historial</Link>
      </nav>

      {loading && (
        <div className="inventory-loading">
          Cargando inventario...
        </div>
      )}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {!loading && !error && products.length === 0 && (
        <div className="inventory-empty">
          No hay ingredientes registrados.
        </div>
      )}

      {!loading && !error && products.length > 0 && (
        <div className="inventory-table-wrapper">
          <table className="inventory-table">
            <thead>
              <tr>
                <th>Ingrediente</th>
                <th>SKU</th>
                <th>Unidad</th>
                <th>Categoría</th>
                <th>País</th>
                <th>Stock actual</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>

            <tbody>
              {products.map((product) => {
                const stockStatus = getStockStatus(
                  product.current_stock,
                );

                return (
                  <tr key={product.id}>
                    <td>
                      <strong>{product.name}</strong>
                    </td>

                    <td>{product.sku}</td>
                    <td>{product.unit}</td>
                    <td>{product.category}</td>
                    <td>{product.country}</td>
                    <td>
                      {product.current_stock} {product.unit}
                    </td>

                    <td>
                      <span className={stockStatus.className}>
                        {stockStatus.label}
                      </span>
                    </td>

                    <td>
                      <div className="inventory-actions">
                        <Link
                          to={`/backoffice/inventory/orders/inbound?productId=${product.id}`}
                        >
                          Entrada
                        </Link>

                        <Link
                          to={`/backoffice/inventory/orders/outbound?productId=${product.id}`}
                        >
                          Salida
                        </Link>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}