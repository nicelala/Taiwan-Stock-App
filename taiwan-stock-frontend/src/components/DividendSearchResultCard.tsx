import type { DividendSearchItem } from "../types/dividend";

type DividendSearchResultCardProps = {
  item: DividendSearchItem;
};

export default function DividendSearchResultCard({
  item,
}: DividendSearchResultCardProps) {
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

        <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
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

          <span
            style={{
              borderRadius: "999px",
              padding: "4px 10px",
              fontSize: "12px",
              fontWeight: 600,
              border: "1px solid #e2e8f0",
              backgroundColor: "#fff",
              color: "#334155",
            }}
          >
            {item.dividend_year} / {item.dividend_year_ad ?? "-"}
          </span>
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
          gap: "12px",
          marginTop: "16px",
          fontSize: "14px",
        }}
      >
        <div>
          <div style={labelStyle}>產業</div>
          <div>{item.industry_name ?? item.industry ?? "-"}</div>
        </div>

        <div>
          <div style={labelStyle}>期別</div>
          <div>{item.period_label ?? "-"}</div>
        </div>

        <div>
          <div style={labelStyle}>現金股利</div>
          <div>{item.cash_dividend_per_share ?? "-"}</div>
        </div>

        <div>
          <div style={labelStyle}>股票股利</div>
          <div>{item.stock_dividend_per_share ?? "-"}</div>
        </div>

        <div>
          <div style={labelStyle}>總股利</div>
          <div>{item.total_dividend_per_share ?? "-"}</div>
        </div>
      </div>
    </div>
  );
}

const labelStyle = {
  color: "#64748b",
  fontSize: "12px",
  marginBottom: "4px",
};