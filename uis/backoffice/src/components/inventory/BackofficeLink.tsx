import { Link } from "react-router-dom";

export default function BackofficeLink() {
  return (
    <Link to="/" className="inventory-backoffice-link">
      ← Volver al Backoffice
    </Link>
  );
}