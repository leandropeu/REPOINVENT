import React from "react";
import Topbar from "../components/Topbar.jsx";
import { api } from "../api.js";

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

export default function Relatorios() {
  return (
    <div className="page">
      <Topbar title="Relatórios" />
      <div className="card">
        <div className="card-title">Exportar CSV (admin)</div>
        <div className="row row-wrap">
          <button className="btn btn-sm btn-primary" onClick={() => download("/reports/units.csv", "units.csv")}>
            Unidades
          </button>
          <button className="btn btn-sm btn-primary" onClick={() => download("/reports/equipment.csv", "equipment.csv")}>
            Equipamentos
          </button>
          <button className="btn btn-sm btn-primary" onClick={() => download("/reports/users.csv", "users.csv")}>
            Usuários
          </button>
          <button className="btn btn-sm" onClick={() => download("/reports/audit.csv", "audit.csv")}>
            Auditoria
          </button>
        </div>
        <div className="hint">Dica: exports usam sua sessão (token). Se der 401, faça login novamente.</div>
      </div>
    </div>
  );
}
