import React from "react";
import { NavLink } from "react-router-dom";

export default function Sidebar() {
  const linkClass = ({ isActive }) => `navlink ${isActive ? "active" : ""}`;
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-title">REPOINVENT</div>
        <div className="brand-sub">Inventário TI</div>
      </div>
      <nav className="nav">
        <NavLink className={linkClass} to="/app/dashboard">
          Dashboard
        </NavLink>
        <NavLink className={linkClass} to="/app/equipamentos">
          Equipamentos
        </NavLink>
        <NavLink className={linkClass} to="/app/unidades">
          Unidades
        </NavLink>
        <NavLink className={linkClass} to="/app/usuarios">
          Usuários
        </NavLink>
        <NavLink className={linkClass} to="/app/auditoria">
          Auditoria
        </NavLink>
      </nav>
    </aside>
  );
}
