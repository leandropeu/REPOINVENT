import React, { useEffect, useMemo, useState } from "react";
import Topbar from "../components/Topbar.jsx";
import Modal from "../components/Modal.jsx";
import { api } from "../api.js";
import { EQUIPMENT_TYPES } from "../constants.js";

const emptyForm = {
  unit_id: "",
  type: "PC",
  name: "",
  brand: "",
  asset_tag: "",
  serial: "",
  imei: "",
  phone_number: "",
  notes: ""
};

function normalizePayload(form) {
  const payload = {
    unit_id: Number(form.unit_id),
    type: form.type,
    name: form.name,
    brand: form.brand || null,
    asset_tag: form.asset_tag || null,
    serial: form.serial || null,
    imei: form.imei || null,
    phone_number: form.phone_number || null,
    notes: form.notes || null
  };
  if (form.type !== "MOBILE") {
    payload.imei = null;
    payload.phone_number = null;
  }
  return payload;
}

export default function Equipamentos() {
  const [items, setItems] = useState([]);
  const [units, setUnits] = useState([]);
  const [q, setQ] = useState("");
  const [unitId, setUnitId] = useState("");
  const [type, setType] = useState("");
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
      const [u, e] = await Promise.all([
        api.units(),
        api.equipment({ q: q || undefined, unit_id: unitId || undefined, type: type || undefined })
      ]);
      setUnits(u);
      setItems(e);
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

  const unitNameById = useMemo(() => Object.fromEntries(units.map((u) => [u.id, u.name])), [units]);

  function openNew() {
    setEditing(null);
    if (!units.length) {
      setError("Cadastre uma unidade antes de inserir equipamento.");
      return;
    }
    setForm({ ...emptyForm, unit_id: units[0]?.id ? String(units[0].id) : "" });
    setOpen(true);
  }

  function openEdit(item) {
    setEditing(item);
    setForm({
      unit_id: String(item.unit_id),
      type: item.type,
      name: item.name || "",
      brand: item.brand || "",
      asset_tag: item.asset_tag || "",
      serial: item.serial || "",
      imei: item.imei || "",
      phone_number: item.phone_number || "",
      notes: item.notes || ""
    });
    setOpen(true);
  }

  async function onSave(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      const payload = normalizePayload(form);
      if (!payload.unit_id) throw new Error("Selecione uma unidade");
      if (!payload.name?.trim()) throw new Error("Informe um nome");
      if (editing) await api.updateEquipment(editing.id, payload);
      else await api.createEquipment(payload);
      setOpen(false);
      await refresh();
    } catch (err) {
      setError(err.message || "Erro");
    } finally {
      setSaving(false);
    }
  }

  async function onRemove(item) {
    if (!confirm(`Remover "${item.name}"?`)) return;
    setError("");
    try {
      await api.deleteEquipment(item.id);
      await refresh();
    } catch (err) {
      setError(err.message || "Erro");
    }
  }

  return (
    <div className="page">
      <Topbar
        title="Equipamentos"
        right={
          <button className="btn btn-sm btn-primary" onClick={openNew}>
            + Novo
          </button>
        }
      />

      {error ? <div className="alert alert-error">{error}</div> : null}

      <div className="card">
        <div className="filters">
          <input className="input-sm" placeholder="Buscar..." value={q} onChange={(e) => setQ(e.target.value)} />
          <select className="input-sm" value={unitId} onChange={(e) => setUnitId(e.target.value)}>
            <option value="">Todas unidades</option>
            {units.map((u) => (
              <option key={u.id} value={u.id}>
                {u.name}
              </option>
            ))}
          </select>
          <select className="input-sm" value={type} onChange={(e) => setType(e.target.value)}>
            <option value="">Todos tipos</option>
            {EQUIPMENT_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
          <button className="btn btn-sm" onClick={refresh}>
            {loading ? "Carregando..." : "Filtrar"}
          </button>
        </div>
      </div>

      <div className="card">
        <div className="table">
          <div className="tr th">
            <div>Unidade</div>
            <div>Tipo</div>
            <div>Nome</div>
            <div>Marca</div>
            <div>Patrimônio</div>
            <div>Série</div>
            <div>Ações</div>
          </div>
          {items.map((it) => (
            <div key={it.id} className="tr">
              <div>{unitNameById[it.unit_id] ?? it.unit_id}</div>
              <div>{it.type}</div>
              <div className="truncate" title={it.name}>
                {it.name}
              </div>
              <div className="truncate" title={it.brand || ""}>
                {it.brand || "-"}
              </div>
              <div>{it.asset_tag || "-"}</div>
              <div>{it.serial || "-"}</div>
              <div className="actions">
                <button className="btn btn-xs" onClick={() => openEdit(it)}>
                  Editar
                </button>
                <button className="btn btn-xs btn-danger" onClick={() => onRemove(it)}>
                  Remover
                </button>
              </div>
            </div>
          ))}
          {!items.length ? <div className="empty">{loading ? "Carregando..." : "Nenhum equipamento."}</div> : null}
        </div>
      </div>

      <Modal
        open={open}
        title={editing ? "Editar equipamento" : "Novo equipamento"}
        onClose={() => (saving ? null : setOpen(false))}
      >
        <form className="form" onSubmit={onSave}>
          <div className="grid grid-2">
            <label className="field">
              <span>Unidade</span>
              <select
                value={form.unit_id}
                onChange={(e) => setForm((f) => ({ ...f, unit_id: e.target.value }))}
              >
                <option value="">Selecione</option>
                {units.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.name}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Tipo</span>
              <select value={form.type} onChange={(e) => setForm((f) => ({ ...f, type: e.target.value }))}>
                {EQUIPMENT_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="grid grid-2">
            <label className="field">
              <span>Nome</span>
              <input value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} />
            </label>
            <label className="field">
              <span>Marca</span>
              <input value={form.brand} onChange={(e) => setForm((f) => ({ ...f, brand: e.target.value }))} />
            </label>
          </div>

          <div className="grid grid-2">
            <label className="field">
              <span>Patrimônio</span>
              <input
                value={form.asset_tag}
                onChange={(e) => setForm((f) => ({ ...f, asset_tag: e.target.value }))}
              />
            </label>
            <label className="field">
              <span>Série</span>
              <input value={form.serial} onChange={(e) => setForm((f) => ({ ...f, serial: e.target.value }))} />
            </label>
          </div>

          {form.type === "MOBILE" ? (
            <div className="grid grid-2">
              <label className="field">
                <span>IMEI</span>
                <input value={form.imei} onChange={(e) => setForm((f) => ({ ...f, imei: e.target.value }))} />
              </label>
              <label className="field">
                <span>Número</span>
                <input
                  value={form.phone_number}
                  onChange={(e) => setForm((f) => ({ ...f, phone_number: e.target.value }))}
                />
              </label>
            </div>
          ) : null}

          <label className="field">
            <span>Observações</span>
            <textarea value={form.notes} onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))} />
          </label>

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
