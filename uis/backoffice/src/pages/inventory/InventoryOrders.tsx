import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listOrders } from "../../services/inventory";
import type { IngredientMovement } from "../../types/inventory";
import BackofficeLink from "../../components/inventory/BackofficeLink";

export default function InventoryOrders() {
  const [orders, setOrders] = useState<IngredientMovement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    const loadOrders = async () => {
      setLoading(true);
      setError("");

      try {
        const data = await listOrders();

        if (active) {
          setOrders(data);
        }
      } catch (err) {
        if (active) {
          setError(
            err instanceof Error
              ? err.message
              : "No se pudo cargar el historial.",
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    loadOrders();

    return () => {
      active = false;
    };
  }, []);

  const formatDate = (date: string) => {
    return new Intl.DateTimeFormat("es-UY", {
      dateStyle: "short",
      timeStyle: "short",
    }).format(new Date(date));
  };

  return (
    <div className="inventory-page">
        <BackofficeLink />
      <div className="inventory-header">
        <div>
          <span className="eyebrow">INVENTARIO</span>
          <h1>Historial de movimientos</h1>
          <p>
            Entradas y salidas registradas en el inventario de
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

      {loading && (
        <div className="inventory-loading">
          Cargando historial...
        </div>
      )}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {!loading && !error && orders.length === 0 && (
        <div className="inventory-empty">
          Todavía no hay movimientos registrados.
        </div>
      )}

      {!loading && !error && orders.length > 0 && (
        <div className="inventory-table-wrapper">
          <table className="inventory-table">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Ingrediente</th>
                <th>Tipo</th>
                <th>Cantidad</th>
                <th>Usuario</th>
              </tr>
            </thead>

            <tbody>
              {orders.map((order) => (
                <tr key={`${order.movement_type}-${order.id}`}>
                  <td>{formatDate(order.created_at)}</td>

                  <td>
                    <strong>{order.ingredient.name}</strong>
                    <div className="inventory-secondary">
                      {order.ingredient.sku}
                    </div>
                  </td>

                  <td>
                    <span
                      className={
                        order.movement_type === "inbound"
                          ? "inventory-movement inventory-movement-inbound"
                          : "inventory-movement inventory-movement-outbound"
                      }
                    >
                      {order.movement_type === "inbound"
                        ? "Entrada"
                        : "Salida"}
                    </span>
                  </td>

                  <td>
                    {order.movement_type === "inbound" ? "+" : "-"}
                    {order.quantity} {order.ingredient.unit}
                  </td>

                  <td>
                    <span className="inventory-user">
                      {order.user_uuid}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}