export type Ingredient = {
  id: number;
  name: string;
  sku: string;
  unit: string;
  category:
    | "meat"
    | "produce"
    | "sauce"
    | "beverage"
    | "packaging"
    | "cleaning";
  country: "CO" | "US";
  current_stock: number;
};

export type IngredientEntryCreate = {
  ingredient_id: number;
  quantity: number;
  supplier_name: string;
  location_id: number;
};

export type IngredientExitCreate = {
  ingredient_id: number;
  quantity: number;
  reason: "consumption" | "waste";
  location_id: number;
};

export type IngredientEntryResponse = IngredientEntryCreate & {
  id: number;
  created_at: string;
  user_uuid: string;
};

export type IngredientExitResponse = IngredientExitCreate & {
  id: number;
  created_at: string;
  user_uuid: string;
};

export type IngredientMovement = {
  id: number;
  movement_type: "inbound" | "outbound";
  quantity: number;
  created_at: string;
  user_uuid: string;
  ingredient: Omit<Ingredient, "current_stock">;
};