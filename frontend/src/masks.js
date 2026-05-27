export function onlyDigits(value) {
  return String(value ?? "").replace(/\D+/g, "");
}

export function applyPattern(digits, pattern) {
  const d = onlyDigits(digits);
  let di = 0;
  let out = "";
  for (let i = 0; i < pattern.length; i++) {
    const p = pattern[i];
    if (p === "#") {
      if (di >= d.length) break;
      out += d[di++];
    } else {
      if (di >= d.length) break;
      out += p;
    }
  }
  return out;
}

export function maskCNPJ(value) {
  return applyPattern(value, "##.###.###/####-##");
}

export function unmaskCNPJ(value) {
  return onlyDigits(value);
}

export function maskCPF(value) {
  return applyPattern(value, "###.###.###-##");
}

export function unmaskCPF(value) {
  return onlyDigits(value);
}

export function maskDateBR(value) {
  return applyPattern(value, "##/##/####");
}

export function unmaskDateBR(value) {
  return onlyDigits(value);
}

// Máscara simples para moeda BRL: digite só números e formata como 1.234,56
export function maskMoneyBR(value) {
  const d = onlyDigits(value);
  if (!d) return "";
  const intValue = Number(d);
  if (!Number.isFinite(intValue)) return "";
  const cents = intValue / 100;
  return cents.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

