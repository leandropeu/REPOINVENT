import React, { useMemo } from "react";

const DEFAULT_COLORS = [
  "#00ffff",
  "#40c4ff",
  "#7c4dff",
  "#00e676",
  "#ffea00",
  "#ff6d00",
  "#ff1744",
  "#00b0ff",
  "#1de9b6",
  "#c6ff00"
];

function polarToCartesian(cx, cy, r, angleDeg) {
  const a = ((angleDeg - 90) * Math.PI) / 180.0;
  return { x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) };
}

function describeArc(cx, cy, r, startAngle, endAngle) {
  const start = polarToCartesian(cx, cy, r, endAngle);
  const end = polarToCartesian(cx, cy, r, startAngle);
  const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
  return `M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArcFlag} 0 ${end.x} ${end.y}`;
}

export default function DonutChart({ title, data = [], size = 220, thickness = 18, colors = DEFAULT_COLORS }) {
  const rows = useMemo(() => {
    const sanitized = (Array.isArray(data) ? data : [])
      .filter((d) => d && typeof d.label === "string")
      .map((d) => ({ label: d.label, value: Number(d.value) || 0 }))
      .filter((d) => d.value > 0);
    return sanitized;
  }, [data]);

  const total = useMemo(() => rows.reduce((acc, r) => acc + r.value, 0), [rows]);

  const cx = size / 2;
  const cy = size / 2;
  const r = Math.max(10, cx - thickness);

  const arcs = useMemo(() => {
    if (!total) return [];
    let a0 = 0;
    return rows.map((row) => {
      const da = (row.value / total) * 360;
      const a1 = a0 + da;
      const path = describeArc(cx, cy, r, a0, a1);
      a0 = a1;
      return { ...row, path };
    });
  }, [rows, total, cx, cy, r]);

  return (
    <div className="chart">
      {title ? <div className="chart-title">{title}</div> : null}
      {!total ? <div className="muted">Sem dados.</div> : null}
      {total ? (
        <div className="donut-wrap">
          <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="donut" aria-label={title || "Donut"}>
            <circle cx={cx} cy={cy} r={r} stroke="rgba(255,255,255,0.08)" strokeWidth={thickness} fill="none" />
            {arcs.map((a, idx) => (
              <path
                key={a.label}
                d={a.path}
                stroke={colors[idx % colors.length]}
                strokeWidth={thickness}
                strokeLinecap="butt"
                fill="none"
              />
            ))}
          </svg>
          <div className="donut-center">
            <div className="donut-total">{total}</div>
            <div className="muted">itens</div>
          </div>
        </div>
      ) : null}
      {total ? (
        <div className="legend">
          {arcs
            .slice()
            .sort((a, b) => b.value - a.value)
            .slice(0, 10)
            .map((a, idx) => (
              <div key={a.label} className="legend-item" title={`${a.label}: ${a.value}`}>
                <span className="legend-dot" style={{ background: colors[idx % colors.length] }} />
                <span className="legend-label">{a.label}</span>
                <span className="legend-value">{a.value}</span>
              </div>
            ))}
        </div>
      ) : null}
    </div>
  );
}

