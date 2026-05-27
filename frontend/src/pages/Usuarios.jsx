import React, { useEffect, useState } from "react";
import Topbar from "../components/Topbar.jsx";
import Modal from "../components/Modal.jsx";
import { api } from "../api.js";

const emptyForm = { name: "", username: "", password: "", is_admin: false, is_active: true };

export default function Usuarios({ me }) {
  const [items, setItems] = useState([]);
  const [recent, setRecent] = useState([]);
  const [q, setQ] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(emptyForm);

  async function refresh() {
    setError("");
    setLoading(true);
    try {
      const [list, r] = await Promise.all([api.users({ q: q || undefined }), api.users({ limit: 10 })]);
      setItems(list);
      setRecent(r);
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

  function openNew() {
    if (!me?.is_admin) {
      setError("Apenas admin pode gerenciar usuários.");
      return;
    }
    setEditing(null);
    setForm(emptyForm);
    setOpen(true);
  }

  function openEdit(u) {
    if (!me?.is_admin) return;
    setEditing(u);
    setForm({
      name: u.name || "",
      username: u.username || "",
      password: "",
      is_admin: !!u.is_admin,
      is_active: !!u.is_active
    });
    setOpen(true);
  }

  async function onSave(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      if (!editing && !form.password) throw new Error("Informe uma senha");
      if (!form.name?.trim()) throw new Error("Informe o nome");
      if (!form.username?.trim()) throw new Error("Informe o usuário");
      const payload = {
        name: form.name,
        username: form.username,
        ...(form.password ? { password: form.password } : {}),
        is_admin: form.is_admin,
        is_active: form.is_active
      };
      if (editing) await api.updateUser(editing.id, payload);
      else await api.createUser({ ...payload, password: form.password });
      setOpen(false);
      await refresh();
    } catch (err) {
      setError(err.message || "Erro");
    } finally {
      setSaving(false);
    }
  }

  async function onRemove(u) {
    if (!me?.is_admin) return;
    if (!confirm(`Remover usuário "${u.username}"?`)) return;
    setError("");
    try {
      await api.deleteUser(u.id);
      await refresh();
    } catch (err) {
      setError(err.message || "Erro");
    }
  }

  return (
    <div className="page">
      <Topbar
        title="Usuários"
        right={
          <button className="btn btn-sm btn-primary" onClick={openNew}>
            + Novo
          </button>
        }
      />

      {error ? <div className="alert alert-error">{error}</div> : null}

      <div className="page-scroll">

      <div className="card">
        <div className="filters filters-2">
          <input className="input-sm" placeholder="Buscar..." value={q} onChange={(e) => setQ(e.target.value)} />
          <button className="btn btn-sm" onClick={refresh}>
            {loading ? "Carregando..." : "Filtrar"}
          </button>
        </div>
      </div>

      <div className="card">
        <div className="table table-users">
          <div className="tr th">
            <div>Nome</div>
            <div>Usuário</div>
            <div>Admin</div>
            <div>Ativo</div>
            <div>Ações</div>
          </div>
          {items.map((u) => (
            <div className="tr" key={u.id}>
              <div className="truncate" title={u.name}>
                {u.name}
              </div>
              <div>{u.username}</div>
              <div>{u.is_admin ? "Sim" : "Não"}</div>
              <div>{u.is_active ? "Sim" : "Não"}</div>
              <div className="actions">
                {me?.is_admin ? (
                  <>
                    <button className="btn btn-xs" onClick={() => openEdit(u)}>
                      Editar
                    </button>
                    <button className="btn btn-xs btn-danger" onClick={() => onRemove(u)}>
                      Remover
                    </button>
                  </>
                ) : (
                  <span className="muted">Sem permissão</span>
                )}
              </div>
            </div>
          ))}
          {!items.length ? <div className="empty">{loading ? "Carregando..." : "Nenhum usuário."}</div> : null}
        </div>
      </div>

      <div className="card">
        <div className="card-title">Usuários inseridos recentemente</div>
        <div className="table table-recent-users">
          <div className="tr th">
            <div>Data</div>
            <div>Nome</div>
            <div>Usuário</div>
            <div>Admin</div>
            <div>Ativo</div>
          </div>
          {recent.map((u) => (
            <div key={`r-${u.id}`} className="tr">
              <div className="truncate" title={u.created_at}>
                {new Date(u.created_at).toLocaleString()}
              </div>
              <div className="truncate" title={u.name}>
                {u.name}
              </div>
              <div className="truncate" title={u.username}>
                {u.username}
              </div>
              <div>{u.is_admin ? "Sim" : "Não"}</div>
              <div>{u.is_active ? "Sim" : "Não"}</div>
            </div>
          ))}
          {!recent.length ? <div className="empty">{loading ? "Carregando..." : "Sem registros recentes."}</div> : null}
        </div>
      </div>

      </div>

      <Modal
        open={open}
        title={editing ? "Editar usuário" : "Novo usuário"}
        onClose={() => (saving ? null : setOpen(false))}
      >
        <form className="form" onSubmit={onSave}>
          <label className="field">
            <span>Nome</span>
            <input value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} />
          </label>
          <div className="grid grid-2">
            <label className="field">
              <span>Usuário</span>
              <input value={form.username} onChange={(e) => setForm((f) => ({ ...f, username: e.target.value }))} />
            </label>
            <label className="field">
              <span>Senha {editing ? "(deixe em branco para manter)" : ""}</span>
              <input
                type="password"
                value={form.password}
                onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
                autoComplete="new-password"
              />
            </label>
          </div>
          <div className="row">
            <label className="check">
              <input
                type="checkbox"
                checked={form.is_admin}
                onChange={(e) => setForm((f) => ({ ...f, is_admin: e.target.checked }))}
              />
              <span>Admin</span>
            </label>
            <label className="check">
              <input
                type="checkbox"
                checked={form.is_active}
                onChange={(e) => setForm((f) => ({ ...f, is_active: e.target.checked }))}
              />
              <span>Ativo</span>
            </label>
          </div>
          <div className="row row-right">
            <button className="btn btn-sm" type="button" onClick={() => setOpen(false)} disabled={saving}>
              Cancelar
            </button>
            <button className="btn btn-sm btn-primary" disabled={saving}>
              {saving ? "Salvando..." : "Salvar"}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
