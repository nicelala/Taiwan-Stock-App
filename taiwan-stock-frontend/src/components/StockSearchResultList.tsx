import type { StockSearchItem } from "../types/stock";
import StockSearchResultCard from "./StockSearchResultCard";

type StockSearchResultListProps = {
  items: StockSearchItem[];
  loading: boolean;
  error: string | null;
  hasSearched: boolean;
  onViewDividends: (item: StockSearchItem) => void;
};

export default function StockSearchResultList({
  items,
  loading,
  error,
  hasSearched,
  onViewDividends,
}: StockSearchResultListProps) {
  if (loading) {
    return <div style={infoBoxStyle}>搜尋中，請稍候...</div>;
  }

  if (error) {
    return (
      <div
        style={{
          ...infoBoxStyle,
          border: "1px solid #fecaca",
          backgroundColor: "#fef2f2",
          color: "#b91c1c",
        }}
      >
        {error}
      </div>
    );
  }

  if (!hasSearched) {
    return <div style={infoBoxStyle}>請輸入關鍵字開始搜尋</div>;
  }

  if (items.length === 0) {
    return <div style={infoBoxStyle}>查無符合條件的股票</div>;
  }

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
        gap: "16px",
      }}
    >
      {items.map((item) => (
        <StockSearchResultCard
          key={`${item.market}-${item.stock_code}`}
          item={item}
          onViewDividends={onViewDividends}
        />
      ))}
    </div>
  );
}

const infoBoxStyle: React.CSSProperties = {
  border: "1px solid #e2e8f0",
  backgroundColor: "#fff",
  borderRadius: "18px",
  padding: "20px",
  color: "#475569",
};