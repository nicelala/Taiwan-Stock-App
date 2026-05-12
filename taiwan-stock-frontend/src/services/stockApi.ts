import type { StockSearchParams, StockSearchResponse } from "../types/stock";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

type ApiErrorDetail =
  | {
      code?: string;
      message?: string;
    }
  | string
  | null;

type ApiErrorResponse = {
  detail?: ApiErrorDetail;
};

function buildQueryString(params: Record<string, string | number | undefined>) {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") return;
    searchParams.set(key, String(value));
  });

  return searchParams.toString();
}

function parseApiError(payload: ApiErrorResponse | null): string {
  if (!payload?.detail) return "查詢失敗，請稍後再試。";

  if (typeof payload.detail === "string") {
    return payload.detail;
  }

  if (payload.detail.message) {
    return payload.detail.message;
  }

  if (payload.detail.code) {
    return payload.detail.code;
  }

  return "查詢失敗，請稍後再試。";
}

export async function searchStocks(params: StockSearchParams): Promise<StockSearchResponse> {
  const queryString = buildQueryString({
    q: params.q,
    market: params.market,
    limit: params.limit ?? 20,
    offset: params.offset ?? 0,
  });

  const response = await fetch(`${API_BASE_URL}/api/v1/stocks/search?${queryString}`, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
  });

  if (!response.ok) {
    let errorPayload: ApiErrorResponse | null = null;

    try {
      errorPayload = await response.json();
    } catch {
      errorPayload = null;
    }

    throw new Error(parseApiError(errorPayload));
  }

  const data = (await response.json()) as StockSearchResponse;
  return data;
}
``