export function precio(valor: number): string {
  return new Intl.NumberFormat("es-GT", { style: "currency", currency: "USD" }).format(valor);
}

export function cambio(pct: number): string {
  const signo = pct > 0 ? "+" : "";
  return `${signo}${pct.toFixed(2)} %`;
}

/** Puntos de un polyline SVG para la serie de cierres, escalados al alto y ancho dados. */
export function puntosSparkline(cierres: number[], ancho = 320, alto = 80): string {
  if (cierres.length < 2) return "";
  const min = Math.min(...cierres);
  const max = Math.max(...cierres);
  const rango = max - min || 1;
  const paso = ancho / (cierres.length - 1);
  return cierres
    .map((c, i) => `${(i * paso).toFixed(1)},${(alto - ((c - min) / rango) * alto).toFixed(1)}`)
    .join(" ");
}
