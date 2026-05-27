import React from "react";

export default function Tabs({ value, onChange, items = [] }) {
  return (
    <div className="seg">
      {items.map((it) => (
        <button
          key={it.value}
          type="button"
          className={`btn btn-xs ${value === it.value ? "btn-primary" : ""}`}
          onClick={() => onChange(it.value)}
        >
          {it.label}
        </button>
      ))}
    </div>
  );
}

