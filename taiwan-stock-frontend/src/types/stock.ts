export type MarketType = "TWSE" | "TPEX";

export type StockSearchItem = {
  stock_code: string;
  market: MarketType;
  company_name: string;
  company_short_name?: string | null;
  industry?: string | null;
  industry_name?: string | null;
  listing_date?: string | null;
};

export type StockSearchResponse = {
  items: StockSearchItem[];
  count: number;
  total_count: number;
};

export type StockSearchParams = {
  q: string;
  market?: MarketType;
  limit?: number;
  offset?: number;
};