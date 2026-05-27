import React, { useEffect, useMemo, useState } from "react";
import Topbar from "../components/Topbar.jsx";
import StatCard from "../components/StatCard.jsx";
import { api } from "../api.js";
import { EQUIPMENT_TYPES } from "../constants.js";

function download(path, filename) {
  const { url, token } = api.reportUrl(path);
  fetch(url, { headers: { Authorization: `Bearer ${token}` } })
    .then(async (res) => {
      if (!res.ok) throw new Error((await res.text()) || "Erro");
      const blob = await res.blob();
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = filename;
      a.click();
      URL.revokeObjectURL(a.href);
    })
    .catch((e) => alert(e.message || "Erro"));
}

export default function Dashboard({ me }) {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");
  const [reportFormat, setReportFormat] = useState("csv");

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

      <div className="card">
        <div className="card-title">Relatórios</div>
        <div className="row row-wrap" style={{ marginBottom: 10 }}>
          <div className="muted" style={{ alignSelf: "center" }}>
            Formato:
          </div>
          <select className="input-sm" value={reportFormat} onChange={(e) => setReportFormat(e.target.value)}>
            <option value="csv">CSV</option>
            <option value="xlsx">Planilha (XLSX)</option>
            <option value="xml">XML</option>
            <option value="pdf">PDF</option>
          </select>
        </div>
        <div className="row row-wrap">
          <button
            className="btn btn-sm btn-primary"
            onClick={() => download(`/reports/units/export/${reportFormat}`, `units.${reportFormat}`)}
          >
            Unidades
          </button>
          <button
            className="btn btn-sm btn-primary"
            onClick={() => download(`/reports/equipment/export/${reportFormat}`, `equipment.${reportFormat}`)}
          >
            Equipamentos
          </button>
          <button
            className="btn btn-sm btn-primary"
            onClick={() => download(`/reports/users/export/${reportFormat}`, `users.${reportFormat}`)}
          >
            Usuários
          </button>
          <button
            className="btn btn-sm"
            onClick={() => download(`/reports/audit/export/${reportFormat}`, `audit.${reportFormat}`)}
          >
            Auditoria
          </button>
        </div>
        {!me?.is_admin ? <div className="hint">Observação: exports exigem permissão de admin.</div> : null}
        <div className="hint">Dica: exports usam sua sessão (token). Se der 401, faça login novamente.</div>
      </div>
    </div>
  );
}
