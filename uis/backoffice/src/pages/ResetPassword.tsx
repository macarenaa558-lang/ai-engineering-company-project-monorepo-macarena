import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

function ResetPassword() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const token = searchParams.get("token") || "";

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();

    setError("");

    if (!token) {
      setError("El enlace de recuperación no es válido.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Las contraseñas no coinciden.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("/auth/reset-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          token,
          new_password: password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "No se pudo restablecer la contraseña.",
        );
      }

      navigate("/login?passwordReset=success");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Ocurrió un error al restablecer la contraseña.",
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
        <h1>Nueva contraseña</h1>

        <p>Ingresá una nueva contraseña para tu cuenta.</p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="password">Nueva contraseña</label>

            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="••••••••"
            />
          </div>

          <div>
            <label htmlFor="confirmPassword">Confirmar contraseña</label>

            <input
              id="confirmPassword"
              type="password"
              required
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              placeholder="••••••••"
            />
          </div>

          {error && (
            <>
              <div className="error-message">{error}</div>

              <p className="auth-footer">
                <Link to="/forgot-password">Solicitar un nuevo enlace</Link>
              </p>
            </>
          )}

          <button
            type="submit"
            className="auth-submit"
            disabled={loading || !token}
          >
            {loading ? "Actualizando..." : "Restablecer contraseña"}
          </button>
        </form>

        <p className="auth-footer">
          <Link to="/login">Volver a iniciar sesión</Link>
        </p>
      </div>
    </div>
  );
}

export default ResetPassword;
