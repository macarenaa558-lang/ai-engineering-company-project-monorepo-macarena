import { authFetch } from "./auth";
import type {
  Ingredient,
  IngredientEntryCreate,
  IngredientExitCreate,
  IngredientEntryResponse,
  IngredientExitResponse,
  IngredientMovement,
} from "../types/inventory";

type FastApiError = {
  detail?: string | Array<{ msg?: string }>;
  message?: string;
};

export class InventoryApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "InventoryApiError";
    this.status = status;
  }
}

const API_URL = import.meta.env.VITE_INVENTORY_API_URL || "";

function extractMessage(
  body: FastApiError | null,
  fallback: string,
): string {
  if (!body) return fallback;

  if (typeof body.detail === "string") {
    return body.detail;
  }

  if (Array.isArray(body.detail)) {
    const messages = body.detail
      .map((item) => item?.msg)
      .filter((item): item is string => Boolean(item));

    if (messages.length > 0) {
      return messages.join(" | ");
    }
  }

  return body.message ?? fallback;
}

async function inventoryFetch<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const headers = new Headers(init.headers);

  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await authFetch(`${API_URL}${path}`, {
    ...init,
    headers,
  });

  if (!response.ok) {
    let body: FastApiError | null = null;

    try {
      body = (await response.json()) as FastApiError;
    } catch {
      body = null;
    }

    throw new InventoryApiError(
      response.status,
      extractMessage(
        body,
        `Error ${response.status}: ${response.statusText}`,
      ),
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export function listProducts() {
  return inventoryFetch<Ingredient[]>("/inventory/products");
}

export function getProduct(id: number) {
  return inventoryFetch<Ingredient>(`/inventory/products/${id}`);
}

export function createInboundOrder(body: IngredientEntryCreate) {
  return inventoryFetch<IngredientEntryResponse>(
    "/inventory/orders/inbound",
    {
      method: "POST",
      body: JSON.stringify(body),
    },
  );
}

export function createOutboundOrder(body: IngredientExitCreate) {
  return inventoryFetch<IngredientExitResponse>(
    "/inventory/orders/outbound",
    {
      method: "POST",
      body: JSON.stringify(body),
    },
  );
}

export function listOrders() {
  return inventoryFetch<IngredientMovement[]>("/inventory/orders");
}