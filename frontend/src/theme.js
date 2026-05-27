const KEY = "theme";

export const THEMES = ["dark", "black", "light"];

export function getTheme() {
  const t = localStorage.getItem(KEY);
  return THEMES.includes(t) ? t : "dark";
}

export function setTheme(theme) {
  const t = THEMES.includes(theme) ? theme : "dark";
  localStorage.setItem(KEY, t);
  applyTheme(t);
}

export function applyTheme(theme = getTheme()) {
  document.documentElement.dataset.theme = theme;
}

export function initTheme() {
  applyTheme(getTheme());
}

