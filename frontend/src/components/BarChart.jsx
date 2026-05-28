import React, { useMemo } from "react";

const DEFAULT_COLORS = ["#00ffff", "#40c4ff", "#7c4dff", "#00e676", "#ffea00", "#ff6d00", "#ff1744"];

export default function BarChart({ title, data = [], maxBars = 12, colors = DEFAULT_COLORS, className = "" }) {
  const rows = useMemo(() => {
    const sanitized = (Array.isArray(data) ? data : [])
      .filter((d) => d && typeof d.label === "string")
      .map((d) => ({ label: d.label, value: Number(d.value) || 0 }))
      .filter((d) => d.value > 0)
      .sort((a, b) => b.value - a.value);
    return sanitized.slice(0, maxBars);
  }, [data, maxBars]);

  const max = useMemo(() => Math.max(1, ...rows.map((r) => r.value)), [rows]);

  return (
    <div className={`chart ${className}`.trim()}>
      {title ? <div className="chart-title">{title}</div> : null}
      {!rows.length ? <div className="muted">Sem dados.</div> : null}
      <div className="bars">
        {rows.map((r, idx) => (
          <div key={r.label} className="bar-row" title={`${r.label}: ${r.value}`}>
            <div className="bar-label">{r.label}</div>
            <div className="bar-track">
              <div
                className="bar-fill"
                style={{
                  width: `${Math.round((r.value / max) * 100)}%`,
                  background: `linear-gradient(90deg, ${colors[idx % colors.length]}, rgba(0,0,0,0))`
                }}
              />
            </div>
            <div className="bar-value">{r.value}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
