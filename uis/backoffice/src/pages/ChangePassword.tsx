import { useState } from "react";
import type { FormEvent } from "react";
import { Link } from "react-router-dom";
import { authFetch } from "../services/auth";

function ChangePassword() {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();

    setMessage("");
    setError("");

    if (newPassword !== confirmPassword) {
      setError("Las contraseñas nuevas no coinciden.");
      return;
    }

    setLoading(true);

    try {
      const response = await authFetch("/auth/change-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "No se pudo cambiar la contraseña.",
        );
      }

      setMessage("Contraseña actualizada correctamente.");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Ocurrió un error al cambiar la contraseña.",
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
        <h1>Cambiar contraseña</h1>

        <p>Ingresá tu contraseña actual y elegí una nueva.</p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="currentPassword">Contraseña actual</label>

            <input
              id="currentPassword"
              type="password"
              required
              value={currentPassword}
              onChange={(event) => setCurrentPassword(event.target.value)}
              placeholder="••••••••"
            />
          </div>

          <div>
            <label htmlFor="newPassword">Nueva contraseña</label>

            <input
              id="newPassword"
              type="password"
              required
              value={newPassword}
              onChange={(event) => setNewPassword(event.target.value)}
              placeholder="••••••••"
            />
          </div>

          <div>
            <label htmlFor="confirmPassword">Confirmar nueva contraseña</label>

            <input
              id="confirmPassword"
              type="password"
              required
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              placeholder="••••••••"
            />
          </div>

          {message && <div className="success-message">{message}</div>}

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="auth-submit" disabled={loading}>
            {loading ? "Actualizando..." : "Cambiar contraseña"}
          </button>
        </form>

        <p className="auth-footer">
          <Link to="/account/profile">Volver a mi perfil</Link>
        </p>
      </div>
    </div>
  );
}

export default ChangePassword;
