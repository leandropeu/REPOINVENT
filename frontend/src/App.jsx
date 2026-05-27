import React, { useEffect, useState } from "react";
import { Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import Login from "./pages/Login.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Equipamentos from "./pages/Equipamentos.jsx";
import Unidades from "./pages/Unidades.jsx";
import Usuarios from "./pages/Usuarios.jsx";
import Auditoria from "./pages/Auditoria.jsx";
import Sidebar from "./components/Sidebar.jsx";
import { api, clearToken, getToken } from "./api.js";
import { getTheme, setTheme, THEMES } from "./theme.js";

function Shell({ children, onLogout, user }) {
  const [theme, setThemeState] = useState(getTheme());

  function onSetTheme(t) {
    setTheme(t);
    setThemeState(getTheme());
  }

  return (
    <div className="shell">
      <Sidebar />
      <main className="main">
        <div className="shell-actions">
          {user ? <div className="muted">UsuÃ¡rio: {user.username}{user.is_admin ? " (admin)" : ""}</div> : null}
          <div className="seg">
            {THEMES.map((t) => (
              <button
                key={t}
                className={`btn btn-xs ${theme === t ? "btn-primary" : ""}`}
                onClick={() => onSetTheme(t)}
                type="button"
                title={`Tema: ${t}`}
              >
                {t === "dark" ? "Dark" : t === "black" ? "Black" : "Light"}
              </button>
            ))}
          </div>
          <button className="btn btn-xs" onClick={onLogout}>
            Sair
          </button>
        </div>
        {children}
      </main>
    </div>
  );
}

function RequireAuth({ children }) {
  const location = useLocation();
  const token = getToken();
  if (!token) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  return children;
}

export default function App() {
  const navigate = useNavigate();
  const [bootError, setBootError] = useState("");
  const [me, setMe] = useState(null);

  useEffect(() => {
    const token = getToken();
    if (!token) return;
    api
      .me()
      .then((u) => setMe(u))
      .catch(() => {
        clearToken();
        setMe(null);
        setBootError("SessÃ£o expirada, faÃ§a login novamente.");
        navigate("/login");
      });
  }, [navigate]);

  async function onLogout() {
    await api.logout();
    navigate("/login");
  }

  return (
    <Routes>
      <Route path="/" element={<Navigate to="/app/dashboard" replace />} />
      <Route path="/login" element={<Login />} />
      <Route
        path="/app/*"
        element={
          <RequireAuth>
            <Shell onLogout={onLogout} user={me}>
              {bootError ? <div className="alert alert-error">{bootError}</div> : null}
              <Routes>
                <Route path="dashboard" element={<Dashboard me={me} />} />
                <Route path="equipamentos" element={<Equipamentos me={me} />} />
                <Route path="unidades" element={<Unidades me={me} />} />
                <Route path="usuarios" element={<Usuarios me={me} />} />
                <Route path="auditoria" element={<Auditoria me={me} />} />
                <Route path="*" element={<Navigate to="/app/dashboard" replace />} />
              </Routes>
            </Shell>
          </RequireAuth>
        }
      />
      <Route path="*" element={<Navigate to="/app/dashboard" replace />} />
    </Routes>
  );
}

