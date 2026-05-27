import React, { useEffect, useState } from "react";
import Topbar from "../components/Topbar.jsx";
import Modal from "../components/Modal.jsx";
import { api } from "../api.js";

export default function Auditoria() {
  const [items, setItems] = useState([]);
  const [q, setQ] = useState("");
  const [entity, setEntity] = useState("");
  const [action, setAction] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState(null);

  async function refresh() {
    setError("");
    setLoading(true);
    try {
      const data = await api.audit({
        q: q || undefined,
        entity: entity || undefined,
        action: action || undefined,
        limit: "500"
      });
      setItems(data);
    } catch (err) {
      setError(err.message || "Erro (somente admin)");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="page">
      <Topbar
        title="Auditoria"
        right={
          <button className="btn btn-sm" onClick={refresh}>
            {loading ? "Carregando..." : "Atualizar"}
          </button>
        }
      />
      {error ? <div className="alert alert-error">{error}</div> : null}

      <div className="card">
        <div className="filters">
          <input className="input-sm" placeholder="Buscar..." value={q} onChange={(e) => setQ(e.target.value)} />
          <select className="input-sm" value={entity} onChange={(e) => setEntity(e.target.value)}>
            <option value="">Todas entidades</option>
            <option value="auth">Auth</option>
            <option value="users">Usuários</option>
            <option value="units">Unidades</option>
            <option value="equipment">Equipamentos</option>
          </select>
          <select className="input-sm" value={action} onChange={(e) => setAction(e.target.value)}>
            <option value="">Todas ações</option>
            <option value="LOGIN">LOGIN</option>
            <option value="CREATE">CREATE</option>
            <option value="UPDATE">UPDATE</option>
            <option value="DELETE">DELETE</option>
          </select>
          <button className="btn btn-sm" onClick={refresh}>
            {loading ? "Carregando..." : "Filtrar"}
          </button>
        </div>
      </div>

      <div className="card">
        <div className="table table-audit">
          <div className="tr th">
            <div>Data</div>
            <div>Usuário</div>
            <div>Ação</div>
            <div>Entidade</div>
            <div>ID</div>
            <div>Resumo</div>
          </div>
          {items.map((it) => (
            <div className="tr tr-click" key={it.id} role="button" tabIndex={0} onClick={() => setSelected(it)}>
              <div className="truncate" title={it.created_at}>
                {new Date(it.created_at).toLocaleString()}
              </div>
              <div className="truncate" title={it.username || ""}>
                {it.username || "-"}
              </div>
              <div>{it.action}</div>
              <div>{it.entity}</div>
              <div>{it.entity_id ?? "-"}</div>
              <div className="truncate" title={it.summary || ""}>
                {it.summary || "-"}
              </div>
            </div>
          ))}
          {!items.length ? <div className="empty">{loading ? "Carregando..." : "Sem eventos."}</div> : null}
        </div>
      </div>

      <Modal open={!!selected} title="Detalhes do evento" onClose={() => setSelected(null)}>
        {selected ? (
          <div className="form">
            <div className="grid grid-2">
              <div className="card mini">
                <div className="card-title">Ação</div>
                <div>{selected.action}</div>
              </div>
              <div className="card mini">
                <div className="card-title">Entidade</div>
                <div>
                  {selected.entity} #{selected.entity_id ?? "-"}
                </div>
              </div>
            </div>
            <div className="card mini">
              <div className="card-title">Resumo</div>
              <div>{selected.summary || "-"}</div>
            </div>
            <div className="grid grid-2">
              <div className="card mini">
                <div className="card-title">Antes</div>
                <pre className="pre">{selected.before_json || "-"}</pre>
              </div>
              <div className="card mini">
                <div className="card-title">Depois</div>
                <pre className="pre">{selected.after_json || "-"}</pre>
              </div>
            </div>
          </div>
        ) : null}
      </Modal>
    </div>
  );
}
