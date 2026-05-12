import { NavLink } from "react-router-dom";

export default function Navbar() {
  return (
    <header
      style={{
        position: "sticky",
        top: 0,
        zIndex: 10,
        backgroundColor: "#ffffff",
        borderBottom: "1px solid #e2e8f0",
        boxShadow: "0 1px 2px rgba(15, 23, 42, 0.04)",
      }}
    >
      <div
        style={{
          maxWidth: "1200px",
          margin: "0 auto",
          padding: "16px 24px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "16px",
          flexWrap: "wrap",
        }}
      >
        <div
          style={{
            fontSize: "20px",
            fontWeight: 800,
            color: "#0f172a",
            whiteSpace: "nowrap",
          }}
        >
          Taiwan Stock App
        </div>

        <nav
          style={{
            display: "flex",
            gap: "12px",
            flexWrap: "wrap",
          }}
        >
          <NavLink
            to="/stocks"
            style={({ isActive }) => ({
              ...linkBaseStyle,
              ...(isActive ? activeLinkStyle : inactiveLinkStyle),
            })}
          >
            股票搜尋
          </NavLink>

          <NavLink
            to="/dividends"
            style={({ isActive }) => ({
              ...linkBaseStyle,
              ...(isActive ? activeLinkStyle : inactiveLinkStyle),
            })}
          >
            股利篩選
          </NavLink>

          <NavLink
            to="/admin/refresh-logs"
            style={({ isActive }) => ({
              ...linkBaseStyle,
              ...(isActive ? activeLinkStyle : inactiveLinkStyle),
            })}
          >
            Refresh Logs
          </NavLink>

          <NavLink
            to="/admin/scheduler"
            style={({ isActive }) => ({
              ...linkBaseStyle,
              ...(isActive ? activeLinkStyle : inactiveLinkStyle),
            })}
          >
            Scheduler
          </NavLink>
        </nav>
      </div>
    </header>
  );
}

const linkBaseStyle: React.CSSProperties = {
  textDecoration: "none",
  padding: "8px 14px",
  borderRadius: "999px",
  fontSize: "14px",
  fontWeight: 600,
  transition: "all 0.2s ease",
};

const activeLinkStyle: React.CSSProperties = {
  backgroundColor: "#0f172a",
  color: "#ffffff",
};

const inactiveLinkStyle: React.CSSProperties = {
  backgroundColor: "#f8fafc",
  color: "#334155",
  border: "1px solid #e2e8f0",
};