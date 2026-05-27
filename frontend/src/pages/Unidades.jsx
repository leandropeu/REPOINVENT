import React, { useEffect, useState } from "react";
import Topbar from "../components/Topbar.jsx";
import Modal from "../components/Modal.jsx";
import { api } from "../api.js";

const emptyForm = { name: "", external_id: "", cnpj: "", address: "" };

export default function Unidades() {
  const [items, setItems] = useState([]);
  const [q, setQ] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [removing, setRemoving] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(emptyForm);

  async function refresh() {
    setError("");
    setLoading(true);
    try {
      const data = await api.units({ q: q || undefined });
      setItems(data);
    } catch (err) {
      setError(err.message || "Erro");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function openNew() {
    setEditing(null);
    setForm(emptyForm);
    setOpen(true);
  }

  function openEdit(u) {
    setEditing(u);
    setForm({
      name: u.name || "",
      external_id: u.external_id || "",
      cnpj: u.cnpj || "",
      address: u.address || ""
    });
    setOpen(true);
  }

  async function onSave(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      if (!form.name?.trim()) throw new Error("Informe o nome");
      const payload = {
        name: form.name,
        external_id: form.external_id || null,
        cnpj: form.cnpj || null,
        address: form.address || null
      };
      if (editing) await api.updateUnit(editing.id, payload);
      else await api.createUnit(payload);
      setOpen(false);
      await refresh();
    } catch (err) {
      setError(err.message || "Erro");
    } finally {
      setSaving(false);
    }
  }

  async function onRemove() {
    if (!editing) return;
    if (!confirm(`Remover unidade "${editing.name}"?`)) return;
    setRemoving(true);
    setError("");
    try {
      await api.deleteUnit(editing.id);
      setOpen(false);
      await refresh();
    } catch (err) {
      setError(err.message || "Erro");
    } finally {
      setRemoving(false);
    }
  }

  return (
    <div className="page">
      <Topbar
        title="Unidades"
        right={
          <button className="btn btn-sm btn-primary" onClick={openNew}>
            + Nova
          </button>
        }
      />

      {error ? <div className="alert alert-error">{error}</div> : null}

      <div className="card">
        <div className="filters filters-2">
          <input className="input-sm" placeholder="Buscar..." value={q} onChange={(e) => setQ(e.target.value)} />
          <button className="btn btn-sm" onClick={refresh}>
            {loading ? "Carregando..." : "Filtrar"}
          </button>
        </div>
      </div>

      <div className="card">
        <div className="table table-units">
          <div className="tr th">
            <div>Unidade</div>
            <div>ID</div>
            <div>CNPJ</div>
            <div>Endereço</div>
            <div>Ações</div>
          </div>
          {items.map((u) => (
            <div className="tr" key={u.id}>
              <div className="truncate" title={u.name}>
                {u.name}
              </div>
              <div>{u.external_id || "-"}</div>
              <div>{u.cnpj || "-"}</div>
              <div className="truncate" title={u.address || ""}>
                {u.address || "-"}
              </div>
              <div className="actions">
                <button className="btn btn-xs" onClick={() => openEdit(u)}>
                  Editar
                </button>
              </div>
            </div>
          ))}
          {!items.length ? <div className="empty">{loading ? "Carregando..." : "Nenhuma unidade."}</div> : null}
        </div>
      </div>

      <Modal
        open={open}
        title={editing ? "Editar unidade" : "Nova unidade"}
        onClose={() => (saving || removing ? null : setOpen(false))}
      >
        <form className="form" onSubmit={onSave}>
          <label className="field">
            <span>Nome</span>
            <input value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} />
          </label>
          <div className="grid grid-2">
            <label className="field">
              <span>ID</span>
              <input
                value={form.external_id}
                onChange={(e) => setForm((f) => ({ ...f, external_id: e.target.value }))}
              />
            </label>
            <label className="field">
              <span>CNPJ</span>
              <input value={form.cnpj} onChange={(e) => setForm((f) => ({ ...f, cnpj: e.target.value }))} />
            </label>
          </div>
          <label className="field">
            <span>Endereço</span>
            <input value={form.address} onChange={(e) => setForm((f) => ({ ...f, address: e.target.value }))} />
          </label>
          <div className="row row-right">
            {editing ? (
              <button
                className="btn btn-sm btn-danger"
                type="button"
                onClick={onRemove}
                disabled={saving || removing}
              >
                {removing ? "Removendo..." : "Deletar"}
              </button>
            ) : null}
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
