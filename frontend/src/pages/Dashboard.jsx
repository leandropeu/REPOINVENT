import React, { useEffect, useMemo, useState } from "react";
import Topbar from "../components/Topbar.jsx";
import StatCard from "../components/StatCard.jsx";
import { api } from "../api.js";
import { EQUIPMENT_TYPES } from "../constants.js";

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;
    api
      .stats()
      .then((data) => mounted && setStats(data))
      .catch((err) => mounted && setError(err.message || "Erro"));
    return () => {
      mounted = false;
    };
  }, []);

  const byType = useMemo(() => stats?.by_type ?? {}, [stats]);

  return (
    <div className="page">
      <Topbar title="Dashboard" />
      {error ? <div className="alert alert-error">{error}</div> : null}
      <div className="grid grid-3">
        <StatCard label="Equipamentos" value={stats?.total_equipment ?? "-"} />
        <StatCard label="Unidades (Evoque)" value={stats?.total_units ?? "-"} />
        <StatCard label="Tipos cadastrados" value={Object.keys(byType).length || "-"} />
      </div>
      <div className="card">
        <div className="card-title">Por tipo</div>
        <div className="chips">
          {EQUIPMENT_TYPES.map((t) => (
            <div key={t} className="chip">
              <div className="chip-label">{t}</div>
              <div className="chip-value">{byType[t] ?? 0}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

