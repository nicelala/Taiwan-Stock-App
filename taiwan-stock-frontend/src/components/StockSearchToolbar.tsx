import type { MarketType } from "../types/stock";

type StockSearchToolbarProps = {
  keyword: string;
  market: "ALL" | MarketType;
  loading: boolean;
  onKeywordChange: (value: string) => void;
  onMarketChange: (value: "ALL" | MarketType) => void;
  onSearch: () => void;
  onReset: () => void;
};

export default function StockSearchToolbar({
  keyword,
  market,
  loading,
  onKeywordChange,
  onMarketChange,
  onSearch,
  onReset,
}: StockSearchToolbarProps) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "1fr 180px 120px 120px",
        gap: "12px",
        marginBottom: "20px",
      }}
    >
      <input
        type="text"
        value={keyword}
        onChange={(e) => onKeywordChange(e.target.value)}
        placeholder="輸入股票代號、公司名稱、公司簡稱"
        style={inputStyle}
        disabled={loading}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            onSearch();
          }
        }}
      />

      <select
        value={market}
        onChange={(e) => onMarketChange(e.target.value as "ALL" | MarketType)}
        style={inputStyle}
        disabled={loading}
      >
        <option value="ALL">全部市場</option>
        <option value="TWSE">TWSE</option>
        <option value="TPEX">TPEX</option>
      </select>

      <button onClick={onSearch} disabled={loading} style={primaryButtonStyle}>
        {loading ? "搜尋中..." : "搜尋"}
      </button>

      <button onClick={onReset} disabled={loading} style={secondaryButtonStyle}>
        重設
      </button>
    </div>
  );
}

const inputStyle: React.CSSProperties = {
  width: "100%",
  height: "42px",
  padding: "0 12px",
  borderRadius: "12px",
  border: "1px solid #cbd5e1",
  outline: "none",
  fontSize: "14px",
  backgroundColor: "#fff",
};

const primaryButtonStyle: React.CSSProperties = {
  height: "42px",
  borderRadius: "12px",
  border: "none",
  backgroundColor: "#0f172a",
  color: "#fff",
  fontSize: "14px",
  cursor: "pointer",
};

const secondaryButtonStyle: React.CSSProperties = {
  height: "42px",
  borderRadius: "12px",
  border: "1px solid #cbd5e1",
  backgroundColor: "#fff",
  color: "#0f172a",
  fontSize: "14px",
  cursor: "pointer",
};