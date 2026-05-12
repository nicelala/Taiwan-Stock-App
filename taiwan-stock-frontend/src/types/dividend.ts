export type MarketType = "TWSE" | "TPEX";
export type SortByType = "cash" | "stock" | "total" | "year" | "code";
export type SortDirType = "asc" | "desc";

export type DividendSearchItem = {
  stock_code: string;
  market: MarketType;
  company_name: string;
  company_short_name?: string | null;
  industry?: string | null;
  industry_name?: string | null;
  dividend_year: number;
  dividend_year_ad?: number | null;
  period_label?: string | null;
  cash_dividend_per_share?: string | null;
  stock_dividend_per_share?: string | null;
  total_dividend_per_share?: string | null;
};

export type DividendSearchResponse = {
  items: DividendSearchItem[];
  count: number;
  total_count: number;
};

export type DividendSearchParams = {
  market?: MarketType;
  year?: number;
  cash_min?: number;
  stock_min?: number;
  total_min?: number;
  sort_by?: SortByType;
  sort_dir?: SortDirType;
  limit?: number;
  offset?: number;
};

export type StockDividendItem = {
  dividend_year: number;
  dividend_year_ad?: number | null;
  belongs_to_year_or_period?: string | null;
  period_label?: string | null;
  resolution_status?: string | null;
  board_approved_date?: string | null;
  shareholder_meeting_date?: string | null;
  cash_dividend_per_share?: string | null;
  stock_dividend_per_share?: string | null;
  total_dividend_per_share?: string | null;
  stock_dividend_rate_pct?: string | null;
  par_value?: string | null;
  updated_at?: string;
};

export type StockDividendResponse = {
  stock_code: string;
  market: MarketType;
  items: StockDividendItem[];
};