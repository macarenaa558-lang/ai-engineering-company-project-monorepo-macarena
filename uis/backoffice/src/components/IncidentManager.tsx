import {
  useCallback,
  useEffect,
  useState,
} from "react";

import type {
  FormEvent,
} from "react";

import {
  authFetch,
} from "../services/auth";


type IncidentStatus =
  | "open"
  | "in_progress"
  | "resolved"
  | "discarded";

type IncidentOrigin =
  | "customer"
  | "branch"
  | "internal";

type IncidentCategory =
  | "equipment_failure"
  | "supply_issue"
  | "customer_complaint"
  | "staff_issue"
  | "facility_issue"
  | "pos_system"
  | "delivery_issue"
  | "other";

type IncidentBranch =
  | "central"
  | "medellin_centro"
  | "medellin_laureles"
  | "medellin_envigado"
  | "medellin_bello"
  | "medellin_itagui"
  | "bogota_chapinero"
  | "bogota_usaquen"
  | "cali_granada"
  | "barranquilla_norte"
  | "miami_doral"
  | "miami_hialeah"
  | "miami_kendall"
  | "orlando_international"
  | "fort_lauderdale";


type Incident = {
  id: number;
  title: string;
  description: string;
  category: IncidentCategory;
  status: IncidentStatus;
  origin: IncidentOrigin;
  branch: IncidentBranch;
  created_at: string;
  updated_at: string;
};


type IncidentSummary = {
  total: number;
  by_status: Record<string, number>;
  by_category: Record<string, number>;
  by_origin: Record<string, number>;
  by_branch: Record<string, number>;
};


type IncidentForm = {
  title: string;
  description: string;
  category: IncidentCategory;
  status: IncidentStatus;
  origin: IncidentOrigin;
  branch: IncidentBranch;
};


type FormErrors = Partial<Record<keyof IncidentForm, string>>;


const STATUSES: {
  value: IncidentStatus;
  label: string;
}[] = [
  {
    value: "open",
    label: "Abierta",
  },
  {
    value: "in_progress",
    label: "En progreso",
  },
  {
    value: "resolved",
    label: "Resuelta",
  },
  {
    value: "discarded",
    label: "Descartada",
  },
];


const ORIGINS: {
  value: IncidentOrigin;
  label: string;
}[] = [
  {
    value: "customer",
    label: "Cliente",
  },
  {
    value: "branch",
    label: "Sucursal",
  },
  {
    value: "internal",
    label: "Interno",
  },
];


const CATEGORIES: {
  value: IncidentCategory;
  label: string;
}[] = [
  {
    value: "equipment_failure",
    label: "Falla de equipamiento",
  },
  {
    value: "supply_issue",
    label: "Problema de suministros",
  },
  {
    value: "customer_complaint",
    label: "Queja de cliente",
  },
  {
    value: "staff_issue",
    label: "Problema de personal",
  },
  {
    value: "facility_issue",
    label: "Problema de instalaciones",
  },
  {
    value: "pos_system",
    label: "Sistema POS",
  },
  {
    value: "delivery_issue",
    label: "Problema de entrega",
  },
  {
    value: "other",
    label: "Otro",
  },
];


const BRANCHES: {
  value: IncidentBranch;
  label: string;
}[] = [
  {
    value: "central",
    label: "Central",
  },
  {
    value: "medellin_centro",
    label: "Medellín Centro",
  },
  {
    value: "medellin_laureles",
    label: "Medellín Laureles",
  },
  {
    value: "medellin_envigado",
    label: "Medellín Envigado",
  },
  {
    value: "medellin_bello",
    label: "Medellín Bello",
  },
  {
    value: "medellin_itagui",
    label: "Medellín Itagüí",
  },
  {
    value: "bogota_chapinero",
    label: "Bogotá Chapinero",
  },
  {
    value: "bogota_usaquen",
    label: "Bogotá Usaquén",
  },
  {
    value: "cali_granada",
    label: "Cali Granada",
  },
  {
    value: "barranquilla_norte",
    label: "Barranquilla Norte",
  },
  {
    value: "miami_doral",
    label: "Miami Doral",
  },
  {
    value: "miami_hialeah",
    label: "Miami Hialeah",
  },
  {
    value: "miami_kendall",
    label: "Miami Kendall",
  },
  {
    value: "orlando_international",
    label: "Orlando International",
  },
  {
    value: "fort_lauderdale",
    label: "Fort Lauderdale",
  },
];


const NEXT_STATUSES: Record<
  IncidentStatus,
  IncidentStatus[]
> = {
  open: [
    "in_progress",
    "discarded",
  ],
  in_progress: [
    "resolved",
    "discarded",
  ],
  resolved: [],
  discarded: [],
};


const EMPTY_FORM: IncidentForm = {
  title: "",
  description: "",
  category: "equipment_failure",
  status: "open",
  origin: "customer",
  branch: "central",
};


function getLabel(
  options: {
    value: string;
    label: string;
  }[],
  value: string,
) {
  return (
    options.find(
      (option) => option.value === value,
    )?.label ?? value
  );
}


async function getApiError(response: Response) {
  try {
    const data = await response.json();

    if (typeof data.detail === "string") {
      return data.detail;
    }

    if (
      data.detail &&
      typeof data.detail === "object"
    ) {
      if (data.detail.message) {
        return data.detail.message;
      }

      if (Array.isArray(data.detail)) {
        return data.detail
          .map((item: { msg?: string }) =>
            item.msg ?? "Dato inválido",
          )
          .join(". ");
      }
    }

    return "La API rechazó la solicitud.";
  } catch {
    return "Ocurrió un error al comunicarse con la API.";
  }
}


export default function IncidentManager() {
  const [form, setForm] =
    useState<IncidentForm>(EMPTY_FORM);

  const [formErrors, setFormErrors] =
    useState<FormErrors>({});

  const [creating, setCreating] =
    useState(false);

  const [createError, setCreateError] =
    useState("");

  const [successMessage, setSuccessMessage] =
    useState("");

  const [incidents, setIncidents] =
    useState<Incident[]>([]);

  const [listLoading, setListLoading] =
    useState(true);

  const [listError, setListError] =
    useState("");

  const [summary, setSummary] =
    useState<IncidentSummary | null>(null);

  const [summaryLoading, setSummaryLoading] =
    useState(true);

  const [summaryError, setSummaryError] =
    useState("");

  const [statusFilter, setStatusFilter] =
    useState("");

  const [originFilter, setOriginFilter] =
    useState("");

  const [branchFilter, setBranchFilter] =
    useState("");

  const [statusUpdateError, setStatusUpdateError] =
    useState("");

  const [statusUpdateSuccess, setStatusUpdateSuccess] =
    useState("");

  const [statusUpdateLoadingId, setStatusUpdateLoadingId] =
    useState<number | null>(null);


  const validateForm = () => {
    const errors: FormErrors = {};

    if (!form.title.trim()) {
      errors.title = "El título es obligatorio.";
    }

    if (form.title.trim().length > 120) {
      errors.title =
        "El título no puede superar los 120 caracteres.";
    }

    if (!form.description.trim()) {
      errors.description =
        "La descripción es obligatoria.";
    }

    if (!form.category) {
      errors.category =
        "La categoría es obligatoria.";
    }

    if (!form.status) {
      errors.status =
        "El estado es obligatorio.";
    }

    if (!form.origin) {
      errors.origin =
        "El origen es obligatorio.";
    }

    if (!form.branch) {
      errors.branch =
        "La sede es obligatoria.";
    }

    setFormErrors(errors);

    return Object.keys(errors).length === 0;
  };


  const loadIncidents = useCallback(async () => {
    setListLoading(true);
    setListError("");

    try {
      const params =
        new URLSearchParams();

      if (statusFilter) {
        params.set(
          "status",
          statusFilter,
        );
      }

      if (originFilter) {
        params.set(
          "origin",
          originFilter,
        );
      }

      if (branchFilter) {
        params.set(
          "branch",
          branchFilter,
        );
      }

      const query =
        params.toString();

      const response =
        await authFetch(
          `/api/incidents${
            query ? `?${query}` : ""
          }`,
        );

      if (!response.ok) {
        throw new Error(
          await getApiError(response),
        );
      }

      const data =
        await response.json();

      setIncidents(data);
    } catch (error) {
      setListError(
        error instanceof Error
          ? error.message
          : "No se pudieron cargar las incidencias.",
      );
    } finally {
      setListLoading(false);
    }
  }, [
    statusFilter,
    originFilter,
    branchFilter,
  ]);


  const loadSummary =
    useCallback(async () => {
      setSummaryLoading(true);
      setSummaryError("");

      try {
        const response =
          await authFetch(
            "/api/incidents/summary",
          );

        if (!response.ok) {
          throw new Error(
            await getApiError(response),
          );
        }

        const data =
          await response.json();

        setSummary(data);
      } catch (error) {
        setSummaryError(
          error instanceof Error
            ? error.message
            : "No se pudo cargar el resumen.",
        );
      } finally {
        setSummaryLoading(false);
      }
    }, []);


  useEffect(() => {
    loadIncidents();
  }, [loadIncidents]);


  useEffect(() => {
    loadSummary();
  }, [loadSummary]);


  const handleCreate =
    async (
      event: FormEvent<HTMLFormElement>,
    ) => {
      event.preventDefault();

      setCreateError("");
      setSuccessMessage("");

      if (!validateForm()) {
        return;
      }

      setCreating(true);

      try {
        const response =
          await authFetch(
            "/api/incidents",
            {
              method: "POST",
              headers: {
                "Content-Type":
                  "application/json",
              },
              body: JSON.stringify({
                ...form,
                title:
                  form.title.trim(),
                description:
                  form.description.trim(),
              }),
            },
          );

        if (!response.ok) {
          throw new Error(
            await getApiError(response),
          );
        }

        setForm(EMPTY_FORM);
        setFormErrors({});

        setSuccessMessage(
          "Incidencia registrada correctamente.",
        );

        await Promise.all([
          loadIncidents(),
          loadSummary(),
        ]);
      } catch (error) {
        setCreateError(
          error instanceof Error
            ? error.message
            : "No se pudo registrar la incidencia.",
        );
      } finally {
        setCreating(false);
      }
    };


  const handleStatusUpdate =
    async (
      incident: Incident,
      newStatus: IncidentStatus,
    ) => {
      const previousStatus =
        incident.status;

      setStatusUpdateError("");
      setStatusUpdateSuccess("");
      setStatusUpdateLoadingId(incident.id);

      setIncidents((current) =>
        current.map((item) =>
          item.id === incident.id
            ? {
                ...item,
                status: newStatus,
              }
            : item,
        ),
      );

      try {
        const response =
          await authFetch(
            `/api/incidents/${incident.id}/status`,
            {
              method: "PATCH",
              headers: {
                "Content-Type":
                  "application/json",
              },
              body: JSON.stringify({
                status: newStatus,
              }),
            },
          );

        if (!response.ok) {
          throw new Error(
            await getApiError(response),
          );
        }

        await loadSummary();

        if (statusFilter) {
          await loadIncidents();
        }

        setStatusUpdateSuccess(
          "Estado actualizado correctamente.",
        );
      } catch (error) {
        setIncidents((current) =>
          current.map((item) =>
            item.id === incident.id
              ? {
                  ...item,
                  status: previousStatus,
                }
              : item,
          ),
        );

        setStatusUpdateError(
          error instanceof Error
            ? error.message
            : "No se pudo actualizar el estado.",
        );
      } finally {
        setStatusUpdateLoadingId(null);
      }
    };


  return (
    <>
      <header className="page-header">
        <div>
          <span className="eyebrow">
            OPERATIONS
          </span>

          <h1>
            Gestor de Incidencias
          </h1>

          <p>
            Registra, consulta y administra
            las incidencias operativas de
            Brasaland en tiempo real.
          </p>
        </div>
      </header>


      <section className="panel">
        <div className="panel-header">
          <div>
            <span className="eyebrow">
              NUEVA INCIDENCIA
            </span>

            <h2>
              Registrar incidencia
            </h2>
          </div>
        </div>


        <form
          className="supplier-form"
          onSubmit={handleCreate}
        >
          <div>
            <label>
              Título
            </label>

            <input
              value={form.title}
              maxLength={120}
              onChange={(event) => {
                setForm((current) => ({
                  ...current,
                  title:
                    event.target.value,
                }));

                setFormErrors(
                  (current) => ({
                    ...current,
                    title: undefined,
                  }),
                );
              }}
            />

            {formErrors.title && (
              <small className="error-message">
                {formErrors.title}
              </small>
            )}
          </div>


          <div>
            <label>
              Categoría
            </label>

            <select
              value={form.category}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  category:
                    event.target
                      .value as IncidentCategory,
                }))
              }
            >
              {CATEGORIES.map(
                (category) => (
                  <option
                    key={category.value}
                    value={category.value}
                  >
                    {category.label}
                  </option>
                ),
              )}
            </select>
          </div>


          <div>
            <label>
              Estado
            </label>

            <select
              value={form.status}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  status:
                    event.target
                      .value as IncidentStatus,
                }))
              }
            >
              {STATUSES.map(
                (status) => (
                  <option
                    key={status.value}
                    value={status.value}
                  >
                    {status.label}
                  </option>
                ),
              )}
            </select>
          </div>


          <div>
            <label>
              Origen
            </label>

            <select
              value={form.origin}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  origin:
                    event.target
                      .value as IncidentOrigin,
                }))
              }
            >
              {ORIGINS.map(
                (origin) => (
                  <option
                    key={origin.value}
                    value={origin.value}
                  >
                    {origin.label}
                  </option>
                ),
              )}
            </select>
          </div>


          <div
            style={
              form.origin === "branch"
                ? {
                    padding: "12px",
                    border:
                      "2px solid #d4a72c",
                    borderRadius:
                      "8px",
                  }
                : undefined
            }
          >
            <label>
              Sede
              {form.origin ===
                "branch" &&
                " — requerida para origen sucursal"}
            </label>

            <select
              value={form.branch}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  branch:
                    event.target
                      .value as IncidentBranch,
                }))
              }
            >
              {BRANCHES.map(
                (branch) => (
                  <option
                    key={branch.value}
                    value={branch.value}
                  >
                    {branch.label}
                  </option>
                ),
              )}
            </select>

            {formErrors.branch && (
              <small className="error-message">
                {formErrors.branch}
              </small>
            )}
          </div>


          <div className="supplier-form-wide">
            <label>
              Descripción
            </label>

            <textarea
              value={form.description}
              onChange={(event) => {
                setForm((current) => ({
                  ...current,
                  description:
                    event.target.value,
                }));

                setFormErrors(
                  (current) => ({
                    ...current,
                    description:
                      undefined,
                  }),
                );
              }}
            />

            {formErrors.description && (
              <small className="error-message">
                {formErrors.description}
              </small>
            )}
          </div>


          <button
            type="submit"
            className="analyze-button"
            disabled={creating}
          >
            {creating
              ? "Registrando..."
              : "Registrar incidencia"}
          </button>
        </form>


        {createError && (
          <div className="error-message">
            {createError}
          </div>
        )}


        {successMessage && (
          <div
            style={{
              marginTop: "16px",
              padding: "12px",
              borderRadius: "8px",
              background:
                "rgba(34, 197, 94, 0.12)",
            }}
          >
            {successMessage}
          </div>
        )}
      </section>


      <section
        className="metrics-grid"
        style={{
          marginTop: "24px",
        }}
      >
        {summaryLoading ? (
          <article className="metric-card">
            <span>
              Resumen
            </span>

            <strong>
              ...
            </strong>
          </article>
        ) : summaryError ? (
          <article className="metric-card">
            <span>
              Resumen no disponible
            </span>

            <button
              type="button"
              onClick={loadSummary}
            >
              Reintentar
            </button>
          </article>
        ) : (
          <>
            <article className="metric-card">
              <span>
                Total
              </span>

              <strong>
                {summary?.total ?? 0}
              </strong>
            </article>


            <article className="metric-card">
              <span>
                Abiertas
              </span>

              <strong>
                {summary?.by_status
                  ?.open ?? 0}
              </strong>
            </article>


            <article className="metric-card">
              <span>
                En progreso
              </span>

              <strong>
                {summary?.by_status
                  ?.in_progress ?? 0}
              </strong>
            </article>


            <article className="metric-card">
              <span>
                Resueltas
              </span>

              <strong>
                {summary?.by_status
                  ?.resolved ?? 0}
              </strong>
            </article>


            <article className="metric-card">
              <span>
                Descartadas
              </span>

              <strong>
                {summary?.by_status
                  ?.discarded ?? 0}
              </strong>
            </article>
          </>
        )}
      </section>


      <section
        className="panel"
        style={{
          marginTop: "24px",
        }}
      >
        <div className="panel-header">
          <div>
            <span className="eyebrow">
              INCIDENTES
            </span>

            <h2>
              Listado de incidencias
            </h2>
          </div>

          <strong>
            {incidents.length}
          </strong>
        </div>


        <div className="supplier-filters">
          <div>
            <label>
              Estado
            </label>

            <select
              value={statusFilter}
              onChange={(event) =>
                setStatusFilter(
                  event.target.value,
                )
              }
            >
              <option value="">
                Todos
              </option>

              {STATUSES.map(
                (status) => (
                  <option
                    key={status.value}
                    value={status.value}
                  >
                    {status.label}
                  </option>
                ),
              )}
            </select>
          </div>


          <div>
            <label>
              Origen
            </label>

            <select
              value={originFilter}
              onChange={(event) =>
                setOriginFilter(
                  event.target.value,
                )
              }
            >
              <option value="">
                Todos
              </option>

              {ORIGINS.map(
                (origin) => (
                  <option
                    key={origin.value}
                    value={origin.value}
                  >
                    {origin.label}
                  </option>
                ),
              )}
            </select>
          </div>


          <div>
            <label>
              Sede
            </label>

            <select
              value={branchFilter}
              onChange={(event) =>
                setBranchFilter(
                  event.target.value,
                )
              }
            >
              <option value="">
                Todas
              </option>

              {BRANCHES.map(
                (branch) => (
                  <option
                    key={branch.value}
                    value={branch.value}
                  >
                    {branch.label}
                  </option>
                ),
              )}
            </select>
          </div>
        </div>


        {statusUpdateError && (
          <div className="error-message">
            {statusUpdateError}
          </div>
        )}

        {statusUpdateSuccess && (
          <div className="success-message">
            {statusUpdateSuccess}
          </div>
        )}


        {listLoading ? (
          <div className="supplier-loading">
            Cargando incidencias...
          </div>
        ) : listError ? (
          <div>
            <div className="error-message">
              {listError}
            </div>

            <button
              type="button"
              className="analyze-button"
              onClick={loadIncidents}
            >
              Reintentar
            </button>
          </div>
        ) : incidents.length === 0 ? (
          <div className="supplier-loading">
            No hay incidencias que coincidan
            con los filtros seleccionados.
          </div>
        ) : (
          <div className="supplier-table-wrapper">
            <table className="supplier-table">
              <thead>
                <tr>
                  <th>
                    Incidencia
                  </th>

                  <th>
                    Categoría
                  </th>

                  <th>
                    Origen
                  </th>

                  <th>
                    Sede
                  </th>

                  <th>
                    Estado
                  </th>

                  <th>
                    Fecha
                  </th>
                </tr>
              </thead>


              <tbody>
                {incidents.map(
                  (incident) => {
                    const nextStatuses =
                      NEXT_STATUSES[
                        incident.status
                      ];

                    return (
                      <tr
                        key={incident.id}
                      >
                        <td>
                          <strong>
                            #{incident.id}{" "}
                            {incident.title}
                          </strong>

                          <span>
                            {
                              incident.description
                            }
                          </span>
                        </td>


                        <td>
                          {getLabel(
                            CATEGORIES,
                            incident.category,
                          )}
                        </td>


                        <td>
                          {getLabel(
                            ORIGINS,
                            incident.origin,
                          )}
                        </td>


                        <td>
                          {getLabel(
                            BRANCHES,
                            incident.branch,
                          )}
                        </td>


                        <td>
                          {statusUpdateLoadingId === incident.id ? (
                            <span>
                              Procesando...
                            </span>
                          ) : nextStatuses.length >
                            0 ? (
                            <select
                              value={
                                incident.status
                              }
                              onChange={(
                                event,
                              ) =>
                                handleStatusUpdate(
                                  incident,
                                  event.target
                                    .value as IncidentStatus,
                                )
                              }
                            >
                              <option
                                value={
                                  incident.status
                                }
                              >
                                {getLabel(
                                  STATUSES,
                                  incident.status,
                                )}
                              </option>

                              {nextStatuses.map(
                                (
                                  status,
                                ) => (
                                  <option
                                    key={
                                      status
                                    }
                                    value={
                                      status
                                    }
                                  >
                                    {getLabel(
                                      STATUSES,
                                      status,
                                    )}
                                  </option>
                                ),
                              )}
                            </select>
                          ) : (
                            <span>
                              {getLabel(
                                STATUSES,
                                incident.status,
                              )}
                            </span>
                          )}
                        </td>


                        <td>
                          {new Date(
                            incident.created_at,
                          ).toLocaleDateString(
                            "es-UY",
                          )}
                        </td>
                      </tr>
                    );
                  },
                )}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  );
}