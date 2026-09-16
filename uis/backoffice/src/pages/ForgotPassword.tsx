import { useState } from "react";
import type { FormEvent } from "react";
import { Link } from "react-router-dom";

function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();

    setError("");
    setMessage("");
    setLoading(true);

    try {
      const response = await fetch("/auth/forgot-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "No se pudo procesar la solicitud.",
        );
      }

      setMessage(
        "Si esa dirección está registrada, recibirás un enlace en breve.",
      );
      setSubmitted(true);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Ocurrió un error al procesar la solicitud.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-brand">B</div>

        <span className="eyebrow">BRASALAND DIGITAL</span>
        <h1>Recuperar contraseña</h1>

        <p>
          Ingresá tu email y te enviaremos un enlace para crear una nueva
          contraseña.
        </p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="email">Email</label>

            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="nombre@ejemplo.com"
              disabled={submitted}
            />
          </div>

          {message && <div className="success-message">{message}</div>}

          {error && <div className="error-message">{error}</div>}

          <button
            type="submit"
            className="auth-submit"
            disabled={loading || submitted}
          >
            {loading
              ? "Enviando..."
              : submitted
                ? "Solicitud enviada"
                : "Enviar enlace"}
          </button>
        </form>

        <p className="auth-footer">
          <Link to="/login">Volver a iniciar sesión</Link>
        </p>
      </div>
    </div>
  );
}

export default ForgotPassword;
