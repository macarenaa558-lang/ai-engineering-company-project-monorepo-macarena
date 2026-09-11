import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Navigate, Route, Routes, useNavigate } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Profile from "./pages/Profile";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import ChangePassword from "./pages/ChangePassword";
import { authFetch, isAuthenticated } from "./services/auth";
import IncidentManager from "./components/IncidentManager";
import "./App.css";


type Supplier = {
  id: number;
  name: string;
  country: "Colombia" | "USA";
  categories: string[];
  rate_per_unit: number;
  currency: "COP" | "USD";
  updated_at: string;
  status: "active" | "suspended";
  contact_email?: string | null;
  notes?: string | null;
};

type SupplierForm = {
  name: string;
  country: "Colombia" | "USA";
  categories: string;
  rate_per_unit: string;
  currency: "COP" | "USD";
  status: "active" | "suspended";
  contact_email: string;
  notes: string;
};

const VALID_CATEGORIES = [
  "carne",
  "verduras_y_hortalizas",
  "salsas_y_condimentos",
  "bebidas",
  "packaging",
  "productos_limpieza",
  "lacteos",
  "carbon_y_combustible",
];

function Backoffice() {
  const navigate = useNavigate();
  const [section, setSection] = useState<"incidents" | "suppliers">(
    "incidents",
  );

  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [supplierLoading, setSupplierLoading] = useState(false);
  const [supplierError, setSupplierError] = useState("");
  const [countryFilter, setCountryFilter] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [showSupplierForm, setShowSupplierForm] = useState(false);

  const [supplierForm, setSupplierForm] = useState<SupplierForm>({
    name: "",
    country: "Colombia",
    categories: "carne",
    rate_per_unit: "",
    currency: "COP",
    status: "active",
    contact_email: "",
    notes: "",
  });

  
  const loadSuppliers = async () => {
    setSupplierLoading(true);
    setSupplierError("");

    const params = new URLSearchParams();

    if (countryFilter) params.set("country", countryFilter);
    if (categoryFilter) params.set("category", categoryFilter);

    const url = params.toString() ? `/suppliers?${params}` : "/suppliers";

    try {
      const response = await authFetch(url);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "No se pudo cargar el directorio.");
      }

      setSuppliers(data);
    } catch (err) {
      setSupplierError(
        err instanceof Error
          ? err.message
          : "Error inesperado al cargar proveedores.",
      );
    } finally {
      setSupplierLoading(false);
    }
  };

  useEffect(() => {
    if (section === "suppliers") {
      loadSuppliers();
    }
  }, [section, countryFilter, categoryFilter]);

  const handleCountryChange = (value: "Colombia" | "USA") => {
    setSupplierForm((current) => ({
      ...current,
      country: value,
      currency: value === "Colombia" ? "COP" : "USD",
    }));
  };

  const handleCreateSupplier = async (event: FormEvent) => {
    event.preventDefault();
    setSupplierError("");

    const categories = supplierForm.categories
      .split(",")
      .map((category) => category.trim())
      .filter(Boolean);

    try {
      const response = await authFetch("/suppliers", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: supplierForm.name,
          country: supplierForm.country,
          categories,
          rate_per_unit: Number(supplierForm.rate_per_unit),
          currency: supplierForm.currency,
          status: supplierForm.status,
          contact_email: supplierForm.contact_email || null,
          notes: supplierForm.notes || null,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "La API rechazó los datos del proveedor.",
        );
      }

      setShowSupplierForm(false);
      setSupplierForm({
        name: "",
        country: "Colombia",
        categories: "carne",
        rate_per_unit: "",
        currency: "COP",
        status: "active",
        contact_email: "",
        notes: "",
      });

      await loadSuppliers();
    } catch (err) {
      setSupplierError(
        err instanceof Error
          ? err.message
          : "No se pudo registrar el proveedor.",
      );
    }
  };

  const handleRateUpdate = async (supplier: Supplier) => {
    const value = window.prompt(
      `Nueva tarifa para ${supplier.name}`,
      String(supplier.rate_per_unit),
    );

    if (value === null) return;

    const newRate = Number(value);

    if (!Number.isFinite(newRate) || newRate <= 0) {
      setSupplierError("La tarifa debe ser un número mayor a cero.");
      return;
    }

    try {
      const response = await authFetch(`/suppliers/${supplier.id}/rate`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          rate_per_unit: newRate,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "No se pudo actualizar la tarifa.");
      }

      await loadSuppliers();
    } catch (err) {
      setSupplierError(
        err instanceof Error ? err.message : "Error al actualizar la tarifa.",
      );
    }
  };

  const handleStatusToggle = async (supplier: Supplier) => {
    const nextStatus = supplier.status === "active" ? "suspended" : "active";

    try {
      const response = await authFetch(`/suppliers/${supplier.id}/status`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          status: nextStatus,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "No se pudo cambiar el estado.");
      }

      await loadSuppliers();
    } catch (err) {
      setSupplierError(
        err instanceof Error ? err.message : "Error al cambiar el estado.",
      );
    }
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">B</div>

          <div>
            <strong>Brasaland</strong>
            <span>Digital Backoffice</span>
          </div>
        </div>

        <nav className="nav-menu">
          <span className="nav-label">OPERATIONS</span>

          <button
            className={`nav-item ${section === "incidents" ? "active" : ""}`}
            onClick={() => setSection("incidents")}
          >
            Incident Analysis
          </button>

          <button
            className={`nav-item ${section === "suppliers" ? "active" : ""}`}
            onClick={() => setSection("suppliers")}
          >
            Supplier Directory
          </button>

          <button
            className="nav-item"
            onClick={() => navigate("/account/profile")}
          >
            Mi perfil
          </button>
        </nav>

        <div className="sidebar-footer">
          Brasaland Digital
          <span>Operations Intelligence</span>
        </div>
      </aside>

      <main className="main-content">
        {section === "incidents" ? (
          <IncidentManager />
        ) : (
          <>
            <header className="page-header">
              <div>
                <span className="eyebrow">PROCUREMENT</span>
                <h1>Supplier Directory</h1>
                <p>
                  Consulta, filtra y administra los proveedores activos y
                  suspendidos de Brasaland.
                </p>
              </div>

              <button
                type="button"
                className="analyze-button supplier-create-button"
                onClick={() => setShowSupplierForm((current) => !current)}
              >
                {showSupplierForm ? "Cerrar formulario" : "Nuevo proveedor"}
              </button>
            </header>

            <section className="supplier-filters">
              <div>
                <label>País</label>
                <select
                  value={countryFilter}
                  onChange={(event) => setCountryFilter(event.target.value)}
                >
                  <option value="">Todos</option>
                  <option value="Colombia">Colombia</option>
                  <option value="USA">USA</option>
                </select>
              </div>

              <div>
                <label>Categoría</label>
                <select
                  value={categoryFilter}
                  onChange={(event) => setCategoryFilter(event.target.value)}
                >
                  <option value="">Todas</option>
                  {VALID_CATEGORIES.map((category) => (
                    <option key={category} value={category}>
                      {category.replaceAll("_", " ")}
                    </option>
                  ))}
                </select>
              </div>
            </section>

            {showSupplierForm && (
              <form className="supplier-form" onSubmit={handleCreateSupplier}>
                <div>
                  <label>Nombre</label>
                  <input
                    required
                    value={supplierForm.name}
                    onChange={(event) =>
                      setSupplierForm((current) => ({
                        ...current,
                        name: event.target.value,
                      }))
                    }
                  />
                </div>

                <div>
                  <label>País</label>
                  <select
                    value={supplierForm.country}
                    onChange={(event) =>
                      handleCountryChange(
                        event.target.value as "Colombia" | "USA",
                      )
                    }
                  >
                    <option value="Colombia">Colombia</option>
                    <option value="USA">USA</option>
                  </select>
                </div>

                <div>
                  <label>Categoría</label>
                  <select
                    value={supplierForm.categories}
                    onChange={(event) =>
                      setSupplierForm((current) => ({
                        ...current,
                        categories: event.target.value,
                      }))
                    }
                  >
                    {VALID_CATEGORIES.map((category) => (
                      <option key={category} value={category}>
                        {category.replaceAll("_", " ")}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label>Tarifa por unidad</label>
                  <input
                    required
                    type="number"
                    min="0.01"
                    step="0.01"
                    value={supplierForm.rate_per_unit}
                    onChange={(event) =>
                      setSupplierForm((current) => ({
                        ...current,
                        rate_per_unit: event.target.value,
                      }))
                    }
                  />
                </div>

                <div>
                  <label>Moneda</label>
                  <input value={supplierForm.currency} disabled />
                </div>

                <div>
                  <label>Estado</label>
                  <select
                    value={supplierForm.status}
                    onChange={(event) =>
                      setSupplierForm((current) => ({
                        ...current,
                        status: event.target.value as "active" | "suspended",
                      }))
                    }
                  >
                    <option value="active">active</option>
                    <option value="suspended">suspended</option>
                  </select>
                </div>

                <div>
                  <label>Email</label>
                  <input
                    type="email"
                    value={supplierForm.contact_email}
                    onChange={(event) =>
                      setSupplierForm((current) => ({
                        ...current,
                        contact_email: event.target.value,
                      }))
                    }
                  />
                </div>

                <div className="supplier-form-wide">
                  <label>Notas</label>
                  <textarea
                    value={supplierForm.notes}
                    onChange={(event) =>
                      setSupplierForm((current) => ({
                        ...current,
                        notes: event.target.value,
                      }))
                    }
                  />
                </div>

                <button type="submit" className="analyze-button">
                  Registrar proveedor
                </button>
              </form>
            )}

            {supplierError && (
              <div className="error-message supplier-error">
                {supplierError}
              </div>
            )}

            {supplierLoading ? (
              <div className="supplier-loading">Cargando proveedores...</div>
            ) : (
              <section className="supplier-table-card">
                <div className="supplier-table-header">
                  <div>
                    <span className="eyebrow">DIRECTORY</span>
                    <h2>Proveedores</h2>
                  </div>

                  <strong>{suppliers.length}</strong>
                </div>

                <div className="supplier-table-wrapper">
                  <table className="supplier-table">
                    <thead>
                      <tr>
                        <th>Proveedor</th>
                        <th>País</th>
                        <th>Categorías</th>
                        <th>Tarifa</th>
                        <th>Estado</th>
                        <th>Acciones</th>
                      </tr>
                    </thead>

                    <tbody>
                      {suppliers.map((supplier) => (
                        <tr key={supplier.id}>
                          <td>
                            <strong>{supplier.name}</strong>
                            {supplier.contact_email && (
                              <span>{supplier.contact_email}</span>
                            )}
                          </td>

                          <td>{supplier.country}</td>

                          <td>
                            <div className="category-badges">
                              {supplier.categories.map((category) => (
                                <span key={category}>
                                  {category.replaceAll("_", " ")}
                                </span>
                              ))}
                            </div>
                          </td>

                          <td>
                            <strong>
                              {supplier.currency}{" "}
                              {supplier.rate_per_unit.toLocaleString()}
                            </strong>
                          </td>

                          <td>
                            <span
                              className={`supplier-status ${supplier.status}`}
                            >
                              {supplier.status}
                            </span>
                          </td>

                          <td>
                            <div className="supplier-actions">
                              <button
                                type="button"
                                onClick={() => handleRateUpdate(supplier)}
                              >
                                Tarifa
                              </button>

                              <button
                                type="button"
                                onClick={() => handleStatusToggle(supplier)}
                              >
                                {supplier.status === "active"
                                  ? "Suspender"
                                  : "Activar"}
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            )}
          </>
        )}
      </main>
    </div>
  );
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      <Route path="/register" element={<Register />} />

      <Route path="/forgot-password" element={<ForgotPassword />} />

      <Route path="/reset-password" element={<ResetPassword />} />

      <Route
        path="/account/profile"
        element={
          <ProtectedRoute>
            <Profile />
          </ProtectedRoute>
        }
      />

      <Route
        path="/account/change-password"
        element={
          <ProtectedRoute>
            <ChangePassword />
          </ProtectedRoute>
        }
      />

      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Backoffice />
          </ProtectedRoute>
        }
      />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
