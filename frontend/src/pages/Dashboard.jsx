import React, { useEffect, useMemo, useState } from "react";
import Topbar from "../components/Topbar.jsx";
import StatCard from "../components/StatCard.jsx";
import BarChart from "../components/BarChart.jsx";
import DonutChart from "../components/DonutChart.jsx";
import { api } from "../api.js";
import { EQUIPMENT_TYPES } from "../constants.js";

function download(path, filename) {
  const { url, token } = api.reportUrl(path);
  fetch(url, { headers: { Authorization: `Bearer ${token}` } })
    .then(async (res) => {
      if (res.status === 401) throw new Error("Sessão expirada, faça login novamente.");
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

async function downloadReport({ resource, format, filename }) {
  const candidates = [`/reports/${resource}/export/${format}`, `/reports/${resource}.${format}`, `/reports/${resource}.csv`];
  const { token } = api.reportUrl("/reports/units.csv");

  for (const path of candidates) {
    const { url } = api.reportUrl(path);
    const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
    if (res.status === 404) continue;
    if (res.status === 401) throw new Error("Sessão expirada, faça login novamente.");
    if (!res.ok) throw new Error((await res.text()) || "Erro");
    const blob = await res.blob();
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    URL.revokeObjectURL(a.href);
    return;
  }

  throw new Error("Relatório não encontrado no backend. Reinicie/atualize o backend.");
}

export default function Dashboard({ me }) {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");
  const [reportFormat, setReportFormat] = useState("csv");
  const [tab, setTab] = useState("resumo");

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
  const chartData = useMemo(
    () => EQUIPMENT_TYPES.map((t) => ({ label: t, value: byType[t] ?? 0 })),
    [byType]
  );

  return (
    <div className="page">
      <Topbar title="Dashboard" />
      {error ? <div className="alert alert-error">{error}</div> : null}
      <div className="card" style={{ padding: 10 }}>
        <div className="seg">
          <button
            type="button"
            className={`btn btn-xs ${tab === "resumo" ? "btn-primary" : ""}`}
            onClick={() => setTab("resumo")}
          >
            Resumo
          </button>
          <button
            type="button"
            className={`btn btn-xs ${tab === "tipos" ? "btn-primary" : ""}`}
            onClick={() => setTab("tipos")}
          >
            Tipos
          </button>
          <button
            type="button"
            className={`btn btn-xs ${tab === "relatorios" ? "btn-primary" : ""}`}
            onClick={() => setTab("relatorios")}
          >
            Relatórios
          </button>
        </div>
      </div>
      <div className="grid grid-3">
        <StatCard label="Equipamentos" value={stats?.total_equipment ?? "-"} />
        <StatCard label="Unidades (Evoque)" value={stats?.total_units ?? "-"} />
        <StatCard label="Tipos cadastrados" value={Object.keys(byType).length || "-"} />
      </div>

      {tab === "resumo" ? (
      <div className="grid grid-2">
        <div className="card">
          <DonutChart title="Distribuição por tipo" data={chartData} />
        </div>
        <div className="card">
          <BarChart title="Top tipos" data={chartData} maxBars={12} />
        </div>
      </div>
      ) : null}

      {tab === "tipos" ? (
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
      ) : null}

      {tab === "relatorios" ? (
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
            onClick={() =>
              downloadReport({ resource: "units", format: reportFormat, filename: `units.${reportFormat}` }).catch((e) =>
                alert(e.message || "Erro")
              )
            }
          >
            Unidades
          </button>
          <button
            className="btn btn-sm btn-primary"
            onClick={() =>
              downloadReport({
                resource: "equipment",
                format: reportFormat,
                filename: `equipment.${reportFormat}`
              }).catch((e) => alert(e.message || "Erro"))
            }
          >
            Equipamentos
          </button>
          <button
            className="btn btn-sm btn-primary"
            onClick={() =>
              downloadReport({ resource: "users", format: reportFormat, filename: `users.${reportFormat}` }).catch((e) =>
                alert(e.message || "Erro")
              )
            }
          >
            Usuários
          </button>
          <button
            className="btn btn-sm"
            onClick={() =>
              downloadReport({ resource: "audit", format: reportFormat, filename: `audit.${reportFormat}` }).catch((e) =>
                alert(e.message || "Erro")
              )
            }
          >
            Auditoria
          </button>
        </div>
        {!me?.is_admin ? <div className="hint">Observação: exports exigem permissão de admin.</div> : null}
        <div className="hint">Dica: exports usam sua sessão (token). Se der 401, faça login novamente.</div>
      </div>
      ) : null}
    </div>
  );
}
