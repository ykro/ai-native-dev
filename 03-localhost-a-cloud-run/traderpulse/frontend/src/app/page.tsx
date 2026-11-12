import { cargarPanel } from "@/lib/api";
import { cambio, precio, puntosSparkline } from "@/lib/formato";

const SUGERIDOS = ["AAPL", "MSFT", "NVDA", "GOOGL", "TSLA"];

type Props = { searchParams: Promise<{ simbolo?: string }> };

export default async function Inicio({ searchParams }: Props) {
  const { simbolo } = await searchParams;
  const resultado = simbolo ? await cargarPanel(simbolo) : null;

  return (
    <main>
      <h1>TraderPulse</h1>
      <p className="sub">Cotización, tendencia del mes y sentimiento de un símbolo. Datos de ejemplo.</p>

      <form action="/" method="get" role="search">
        <input
          name="simbolo"
          aria-label="Símbolo"
          placeholder="Escribe un símbolo, por ejemplo NVDA"
          defaultValue={simbolo ?? ""}
          maxLength={10}
          required
        />
        <button type="submit">Analizar</button>
      </form>

      {!resultado && (
        <nav className="chips" aria-label="Símbolos sugeridos">
          {SUGERIDOS.map((s) => (
            <a key={s} href={`/?simbolo=${s}`}>
              {s}
            </a>
          ))}
        </nav>
      )}

      {resultado && !resultado.ok && (
        <section className="tarjeta" role="alert">
          <p className="aviso">{resultado.error.mensaje}</p>
        </section>
      )}

      {resultado?.ok && <PanelSimbolo panel={resultado.panel} />}
    </main>
  );
}

function PanelSimbolo({ panel }: { panel: import("@/lib/api").Panel }) {
  const { cotizacion: c, historico, sentimiento: s } = panel;
  const tono = c.cambio_pct >= 0 ? "sube" : "baja";
  return (
    <>
      <section className="tarjeta" aria-label={`Cotización de ${c.simbolo}`}>
        <small>
          {c.simbolo} · {c.nombre} · cierre del {c.fecha}
        </small>
        <p className="precio" data-testid="precio">
          {precio(c.precio)}
        </p>
        <p className={tono} data-testid="cambio">
          {cambio(c.cambio_pct)} contra el cierre anterior
        </p>
        <svg width="100%" viewBox="0 0 320 80" role="img" aria-label="Cierres del último mes">
          <polyline
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            points={puntosSparkline(historico.map((p) => p.cierre))}
          />
        </svg>
      </section>
      <section className="tarjeta" aria-label="Sentimiento">
        <span className="etiqueta" data-testid="sentimiento">
          {s.sentimiento}
        </span>
        <p>{s.justificacion}</p>
        <small>Fuente: {s.fuente}</small>
      </section>
    </>
  );
}
