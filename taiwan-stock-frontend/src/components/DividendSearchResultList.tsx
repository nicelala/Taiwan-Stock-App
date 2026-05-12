import type { DividendSearchItem } from "../types/dividend";
import DividendSearchResultCard from "./DividendSearchResultCard";

type DividendSearchResultListProps = {
  items: DividendSearchItem[];
  loading: boolean;
  error: string | null;
  hasSearched: boolean;
};

export default function DividendSearchResultList({
  items,
  loading,
  error,
  hasSearched,
}: DividendSearchResultListProps) {
  if (loading) {
    return <div style={infoBoxStyle}>查詢中，請稍候...</div>;
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
    return <div style={infoBoxStyle}>請設定條件後開始查詢</div>;
  }

  if (items.length === 0) {
    return <div style={infoBoxStyle}>查無符合條件的股利資料</div>;
  }

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))",
        gap: "16px",
      }}
    >
      {items.map((item, index) => (
        <DividendSearchResultCard
          key={`${item.market}-${item.stock_code}-${item.dividend_year}-${item.period_label ?? "p"}-${index}`}
          item={item}
        />
      ))}
    </div>
  );
}

const infoBoxStyle = {
  border: "1px solid #e2e8f0",
  backgroundColor: "#fff",
  borderRadius: "18px",
  padding: "20px",
  color: "#475569",
};