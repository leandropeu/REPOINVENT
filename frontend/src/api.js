const API_BASE = "http://127.0.0.1:8010";

function buildQuery(params = {}) {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v === undefined || v === null) return;
    if (typeof v === "string" && v.trim() === "") return;
    qs.set(k, String(v));
  });
  const s = qs.toString();
  return s ? `?${s}` : "";
}

export function getToken() {
  return localStorage.getItem("access_token");
}

export function getRefreshToken() {
  return localStorage.getItem("refresh_token");
}

export function setTokens(accessToken, refreshToken) {
  if (accessToken) localStorage.setItem("access_token", accessToken);
  if (refreshToken) localStorage.setItem("refresh_token", refreshToken);
}

export function clearToken() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

async function refreshAccessToken() {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return false;
  const res = await fetch(`${API_BASE}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken })
  });
  if (!res.ok) return false;
  const data = await res.json();
  setTokens(data.access_token, data.refresh_token);
  return true;
}

async function request(path, { method = "GET", body, auth = true, retry = true } = {}) {
  const headers = {};
  if (auth) {
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }
  if (!(body instanceof FormData) && body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body instanceof FormData ? body : body !== undefined ? JSON.stringify(body) : undefined
  });

  if (!res.ok) {
    if (res.status === 401 && auth && retry) {
      const refreshed = await refreshAccessToken();
      if (refreshed) {
        return request(path, { method, body, auth, retry: false });
      }
      clearToken();
      if (window.location.pathname !== "/login") window.location.assign("/login");
      throw new Error("Sessao expirada, faca login novamente.");
    }
    let detail = "Erro";
    try {
      const data = await res.json();
      if (typeof data?.detail === "string") detail = data.detail;
      else if (Array.isArray(data?.detail) && data.detail[0]?.msg) detail = data.detail[0].msg;
    } catch {
      // ignore
    }
    throw new Error(detail);
  }

  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  async login(username, password) {
    const body = new URLSearchParams();
    body.set("username", username);
    body.set("password", password);
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: body.toString()
    });
    if (!res.ok) {
      if (res.status === 401) throw new Error("Credenciais invalidas");
      let detail = "Erro";
      try {
        const data = await res.json();
        if (typeof data?.detail === "string") detail = data.detail;
      } catch {
        // ignore
      }
      throw new Error(detail);
    }
    return res.json();
  },
  async logout() {
    const refreshToken = getRefreshToken();
    if (refreshToken) {
      await fetch(`${API_BASE}/auth/logout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken })
      }).catch(() => null);
    }
    clearToken();
  },
  me() {
    return request("/auth/me");
  },
  stats() {
    return request("/stats");
  },
  units(params = {}) {
    return request(`/units${buildQuery(params)}`);
  },
  createUnit(payload) {
    return request("/units", { method: "POST", body: payload });
  },
  updateUnit(id, payload) {
    return request(`/units/${id}`, { method: "PUT", body: payload });
  },
  deleteUnit(id) {
    return request(`/units/${id}`, { method: "DELETE" });
  },
  equipment(params = {}) {
    return request(`/equipment${buildQuery(params)}`);
  },
  createEquipment(payload) {
    return request("/equipment", { method: "POST", body: payload });
  },
  updateEquipment(id, payload) {
    return request(`/equipment/${id}`, { method: "PUT", body: payload });
  },
  deleteEquipment(id) {
    return request(`/equipment/${id}`, { method: "DELETE" });
  },
  users(params = {}) {
    return request(`/users${buildQuery(params)}`);
  },
  createUser(payload) {
    return request("/users", { method: "POST", body: payload });
  },
  updateUser(id, payload) {
    return request(`/users/${id}`, { method: "PUT", body: payload });
  },
  deleteUser(id) {
    return request(`/users/${id}`, { method: "DELETE" });
  },
  audit(params = {}) {
    return request(`/audit${buildQuery(params)}`);
  },
  reportUrl(path) {
    const token = getToken();
    if (!token) throw new Error("Sem token");
    const url = new URL(`${API_BASE}${path}`);
    return { url: url.toString(), token };
  }
};

