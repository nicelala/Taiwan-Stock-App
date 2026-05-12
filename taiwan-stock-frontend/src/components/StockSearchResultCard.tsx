import type { StockSearchItem } from "../types/stock";

type StockSearchResultCardProps = {
  item: StockSearchItem;
  onViewDividends: (item: StockSearchItem) => void;
};

export default function StockSearchResultCard({
  item,
  onViewDividends,
}: StockSearchResultCardProps) {
  const marketStyle =
    item.market === "TWSE"
      ? {
          backgroundColor: "#dbeafe",
          color: "#1d4ed8",
          border: "1px solid #bfdbfe",
        }
      : {
          backgroundColor: "#d1fae5",
          color: "#047857",
          border: "1px solid #a7f3d0",
        };

  return (
    <div
      style={{
        border: "1px solid #e2e8f0",
        borderRadius: "18px",
        padding: "16px",
        backgroundColor: "#fff",
        boxShadow: "0 1px 2px rgba(15, 23, 42, 0.04)",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: "12px",
          alignItems: "flex-start",
        }}
      >
        <div>
          <div style={{ fontSize: "18px", fontWeight: 700 }}>
            {item.stock_code} {item.company_short_name ?? ""}
          </div>
          <div style={{ fontSize: "14px", color: "#64748b", marginTop: "4px" }}>
            {item.company_name}
          </div>
        </div>

        <span
          style={{
            ...marketStyle,
            borderRadius: "999px",
            padding: "4px 10px",
            fontSize: "12px",
            fontWeight: 600,
            whiteSpace: "nowrap",
          }}
        >
          {item.market}
        </span>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
          gap: "12px",
          marginTop: "16px",
          fontSize: "14px",
        }}
      >
        <div>
          <div style={labelStyle}>產業代碼</div>
          <div>{item.industry ?? "-"}</div>
        </div>

        <div>
          <div style={labelStyle}>產業名稱</div>
          <div>{item.industry_name ?? "-"}</div>
        </div>

        <div>
          <div style={labelStyle}>上市 / 上櫃日</div>
          <div>{item.listing_date ?? "-"}</div>
        </div>
      </div>

      <div
        style={{
          marginTop: "16px",
          display: "flex",
          justifyContent: "flex-end",
        }}
      >
        <button
          onClick={() => onViewDividends(item)}
          style={actionButtonStyle}
        >
          查看股利
        </button>
      </div>
    </div>
  );
}

const labelStyle: React.CSSProperties = {
  color: "#64748b",
  fontSize: "12px",
  marginBottom: "4px",
};

const actionButtonStyle: React.CSSProperties = {
  height: "38px",
  borderRadius: "12px",
  border: "none",
  backgroundColor: "#0f172a",
  color: "#fff",
  fontSize: "14px",
  cursor: "pointer",
  padding: "0 16px",
};