import type { MarketType, SortByType, SortDirType } from "../types/dividend";

type MarketFilter = "ALL" | MarketType;

type DividendSearchToolbarProps = {
  market: MarketFilter;
  year: string;
  cashMin: string;
  stockMin: string;
  totalMin: string;
  sortBy: SortByType;
  sortDir: SortDirType;
  loading: boolean;
  onMarketChange: (value: MarketFilter) => void;
  onYearChange: (value: string) => void;
  onCashMinChange: (value: string) => void;
  onStockMinChange: (value: string) => void;
  onTotalMinChange: (value: string) => void;
  onSortByChange: (value: SortByType) => void;
  onSortDirChange: (value: SortDirType) => void;
  onSearch: () => void;
  onReset: () => void;
};

export default function DividendSearchToolbar({
  market,
  year,
  cashMin,
  stockMin,
  totalMin,
  sortBy,
  sortDir,
  loading,
  onMarketChange,
  onYearChange,
  onCashMinChange,
  onStockMinChange,
  onTotalMinChange,
  onSortByChange,
  onSortDirChange,
  onSearch,
  onReset,
}: DividendSearchToolbarProps) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
        gap: "12px",
        marginBottom: "20px",
      }}
    >
      <select
        value={market}
        onChange={(e) => onMarketChange(e.target.value as MarketFilter)}
        style={inputStyle}
        disabled={loading}
      >
        <option value="ALL">全部市場</option>
        <option value="TWSE">TWSE</option>
        <option value="TPEX">TPEX</option>
      </select>

      <input
        type="text"
        value={year}
        onChange={(e) => onYearChange(e.target.value)}
        placeholder="股利年度（例如 114）"
        style={inputStyle}
        disabled={loading}
      />

      <input
        type="text"
        value={cashMin}
        onChange={(e) => onCashMinChange(e.target.value)}
        placeholder="現金股利下限"
        style={inputStyle}
        disabled={loading}
      />

      <input
        type="text"
        value={stockMin}
        onChange={(e) => onStockMinChange(e.target.value)}
        placeholder="股票股利下限"
        style={inputStyle}
        disabled={loading}
      />

      <input
        type="text"
        value={totalMin}
        onChange={(e) => onTotalMinChange(e.target.value)}
        placeholder="總股利下限"
        style={inputStyle}
        disabled={loading}
      />

      <select
        value={sortBy}
        onChange={(e) => onSortByChange(e.target.value as SortByType)}
        style={inputStyle}
        disabled={loading}
      >
        <option value="cash">現金股利</option>
        <option value="stock">股票股利</option>
        <option value="total">總股利</option>
        <option value="year">年度</option>
        <option value="code">代號</option>
      </select>

      <select
        value={sortDir}
        onChange={(e) => onSortDirChange(e.target.value as SortDirType)}
        style={inputStyle}
        disabled={loading}
      >
        <option value="desc">由大到小</option>
        <option value="asc">由小到大</option>
      </select>

      <div style={{ display: "flex", gap: "12px" }}>
        <button onClick={onSearch} disabled={loading} style={primaryButtonStyle}>
          {loading ? "查詢中..." : "套用條件"}
        </button>

        <button onClick={onReset} disabled={loading} style={secondaryButtonStyle}>
          重設
        </button>
      </div>
    </div>
  );
}

const inputStyle = {
  width: "100%",
  height: "42px",
  padding: "0 12px",
  borderRadius: "12px",
  border: "1px solid #cbd5e1",
  outline: "none",
  fontSize: "14px",
  backgroundColor: "#fff",
};

const primaryButtonStyle = {
  height: "42px",
  borderRadius: "12px",
  border: "none",
  backgroundColor: "#0f172a",
  color: "#fff",
  fontSize: "14px",
  cursor: "pointer",
  padding: "0 16px",
};

const secondaryButtonStyle = {
  height: "42px",
  borderRadius: "12px",
  border: "1px solid #cbd5e1",
  backgroundColor: "#fff",
  color: "#0f172a",
  fontSize: "14px",
  cursor: "pointer",
  padding: "0 16px",
};