import "server-only";
import createClient from "openapi-fetch";
import type { components, paths } from "./api-schema";

export type Panel = components["schemas"]["Panel"];
export type ErrorApi = components["schemas"]["ErrorApi"];

/**
 * Cliente del BFF. Corre solo en el servidor de Next.js: la URL y el token
 * se leen en tiempo de ejecución (Cloud Run los inyecta), nunca en el build.
 */
export function clienteBff() {
  const baseUrl = process.env.API_URL;
  if (!baseUrl) throw new Error("Falta API_URL en el entorno del servidor.");
  return createClient<paths>({
    baseUrl,
    headers: { "X-TraderPulse-Token": process.env.TRADERPULSE_TOKEN ?? "" },
  });
}

export type ResultadoPanel =
  | { ok: true; panel: Panel }
  | { ok: false; estado: number; error: ErrorApi };

export async function cargarPanel(simbolo: string): Promise<ResultadoPanel> {
  const { data, error, response } = await clienteBff().GET("/api/v1/panel/{simbolo}", {
    params: { path: { simbolo } },
    cache: "no-store",
  });
  if (data) return { ok: true, panel: data };
  // 401 y 404 traen ErrorApi; 422 trae el formato de validación de FastAPI.
  // El contrato obliga a distinguirlos: el compilador no deja leer "codigo" de un 422.
  const tipado = error && "codigo" in error ? error : null;
  return {
    ok: false,
    estado: response.status,
    error: tipado ?? { codigo: "error_bff", mensaje: `El BFF respondió ${response.status}.` },
  };
}
