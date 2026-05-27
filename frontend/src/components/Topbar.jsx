import React from "react";

export default function Topbar({ title, right }) {
  return (
    <div className="topbar">
      <div className="topbar-title">{title}</div>
      <div className="topbar-right">{right}</div>
    </div>
  );
}

