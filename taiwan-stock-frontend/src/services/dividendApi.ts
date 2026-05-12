import type {
  DividendSearchParams,
  DividendSearchResponse,
  MarketType,
  StockDividendResponse,
} from "../types/dividend";

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

export async function searchDividends(
  params: DividendSearchParams
): Promise<DividendSearchResponse> {
  const queryString = buildQueryString({
    market: params.market,
    year: params.year,
    cash_min: params.cash_min,
    stock_min: params.stock_min,
    total_min: params.total_min,
    sort_by: params.sort_by ?? "total",
    sort_dir: params.sort_dir ?? "desc",
    limit: params.limit ?? 20,
    offset: params.offset ?? 0,
  });

  const response = await fetch(`${API_BASE_URL}/api/v1/dividends/search?${queryString}`, {
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

  const data = (await response.json()) as DividendSearchResponse;
  return data;
}

export async function getStockDividends(params: {
  stockCode: string;
  market?: MarketType;
  yearFrom?: number;
  yearTo?: number;
}): Promise<StockDividendResponse> {
  const queryString = buildQueryString({
    market: params.market,
    year_from: params.yearFrom,
    year_to: params.yearTo,
  });

  const url = `${API_BASE_URL}/api/v1/stocks/${params.stockCode}/dividends${
    queryString ? `?${queryString}` : ""
  }`;

  const response = await fetch(url, {
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

  const data = (await response.json()) as StockDividendResponse;
  return data;
}