"""Juez de despliegue: lo que Cloud Run espera de las imágenes y de la config, verificado en local.

Construye las dos imágenes, las corre como las correría Cloud Run y revisa la definición de
cada servicio. No llama a GCP. Se escribió antes que los Dockerfiles y no se edita.

Uso (desde 03-localhost-a-cloud-run/):  uv run --with pyyaml python juez/juez_contenedor.py
Sale con 0 si todas las verificaciones pasan.
"""
from __future__ import annotations

import re
import secrets
import subprocess
import sys
import tarfile
import time
import urllib.request
from pathlib import Path

import yaml

AQUI = Path(__file__).resolve().parents[1]
BACK, FRONT, GCP = AQUI / "traderpulse/backend", AQUI / "traderpulse/frontend", AQUI / "gcp"
IMG_API, IMG_WEB, RED = "traderpulse-juez-api", "traderpulse-juez-web", "traderpulse-juez"
LIMITE_MB = {"api": 350, "web": 450}

CANARIO = f"canario-{secrets.token_hex(6)}"  # se escribe en .env locales: no debe llegar a la imagen
TOKEN = f"token-juez-{secrets.token_hex(6)}"  # se pasa en tiempo de ejecución: no debe llegar al navegador

resultados: list[tuple[str, bool, str]] = []

DEPENDIENTES = {
    "api": ["no corre como root", "ningún .env ni su contenido entra a la imagen",
            f"la imagen pesa menos de {LIMITE_MB['api']} MB", "escucha en el puerto que dice $PORT",
            "atiende SIGTERM en menos de 5 s"],
    "web": ["no corre como root", "ningún .env ni su contenido entra a la imagen",
            f"la imagen pesa menos de {LIMITE_MB['web']} MB", "escucha en $PORT y lee API_URL al arrancar",
            "el token no llega al navegador", "atiende SIGTERM en menos de 5 s"],
    "yaml": ["no define PORT (Cloud Run lo inyecta)", "el token viene de Secret Manager",
             "usa una cuenta de servicio propia", "tiene startup probe HTTP",
             "sin IDs de proyecto escritos a mano"],
}


def sin_verificar(nombre: str, grupo: str, motivo: str) -> None:
    for chequeo in DEPENDIENTES[grupo]:
        anotar(f"{nombre} · {chequeo}", False, motivo)


def anotar(nombre: str, ok: bool, detalle: str = "") -> bool:
    resultados.append((nombre, ok, detalle))
    return ok


def sh(*cmd: str, timeout: int = 900) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def esperar_http(url: str, segundos: int = 40) -> tuple[int, str]:
    fin = time.time() + segundos
    while time.time() < fin:
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                return r.status, r.read().decode("utf-8", "replace")
        except Exception:  # noqa: BLE001 - el contenedor puede tardar en arrancar
            time.sleep(1)
    return 0, ""


def construir(nombre: str, contexto: Path, imagen: str) -> bool:
    if not (contexto / "Dockerfile").exists():
        return anotar(f"{nombre} · la imagen se construye", False, "no hay Dockerfile")
    r = sh("docker", "build", "-q", "-t", imagen, str(contexto))
    return anotar(f"{nombre} · la imagen se construye", r.returncode == 0, r.stderr[-600:])


def no_root(nombre: str, imagen: str) -> None:
    r = sh("docker", "run", "--rm", "--entrypoint", "id", imagen, "-u")
    uid = r.stdout.strip()
    anotar(f"{nombre} · no corre como root", r.returncode == 0 and uid not in ("", "0"),
           f"uid efectivo: {uid or r.stderr.strip()[:200]}")


def sin_secretos_en_imagen(nombre: str, imagen: str) -> None:
    sh("docker", "rm", "-f", "traderpulse-juez-export")
    sh("docker", "create", "--name", "traderpulse-juez-export", imagen)
    tar = AQUI / ".juez-export.tar"
    sh("docker", "export", "-o", str(tar), "traderpulse-juez-export")
    sh("docker", "rm", "-f", "traderpulse-juez-export")
    hallazgos: list[str] = []
    with tarfile.open(tar) as t:
        for m in t:
            base = Path(m.name).name
            if m.isfile() and re.fullmatch(r"\.env(\..+)?", base) and "node_modules" not in m.name:
                hallazgos.append(f"archivo {m.name}")
            if m.isfile() and m.size < 4_000_000 and not m.name.startswith(("usr/", "lib/", "etc/")):
                datos = t.extractfile(m)
                if datos and CANARIO.encode() in datos.read():
                    hallazgos.append(f"valor de .env dentro de {m.name}")
    tar.unlink(missing_ok=True)
    anotar(f"{nombre} · ningún .env ni su contenido entra a la imagen", not hallazgos,
           "; ".join(sorted(set(hallazgos))[:5]))


def tamano(nombre: str, imagen: str, clave: str) -> None:
    r = sh("docker", "image", "inspect", "-f", "{{.Size}}", imagen)
    mb = int(r.stdout.strip() or 0) / 1_000_000
    anotar(f"{nombre} · la imagen pesa menos de {LIMITE_MB[clave]} MB", 0 < mb < LIMITE_MB[clave],
           f"{mb:.0f} MB")


def se_detiene_rapido(nombre: str, contenedor: str) -> None:
    inicio = time.time()
    sh("docker", "stop", "-t", "10", contenedor)
    seg = time.time() - inicio
    anotar(f"{nombre} · atiende SIGTERM en menos de 5 s", seg < 5, f"{seg:.1f} s")


def revisar_servicio(nombre: str, archivo: Path, con_token: bool) -> None:
    if not archivo.exists():
        sin_verificar(nombre, "yaml", f"no existe gcp/{archivo.name}")
        return
    texto = archivo.read_text(encoding="utf-8")
    try:
        doc = yaml.safe_load(texto)
        spec = doc["spec"]["template"]["spec"]
        cont = spec["containers"][0]
    except Exception as e:  # noqa: BLE001
        sin_verificar(nombre, "yaml", f"{archivo.name} no es un servicio de Cloud Run: {e}"[:200])
        return
    env = {e["name"]: e for e in cont.get("env", [])}
    anotar(f"{nombre} · no define PORT (Cloud Run lo inyecta)", "PORT" not in env,
           "PORT está en env" if "PORT" in env else "")
    if con_token:
        token = env.get("TRADERPULSE_TOKEN", {})
        ref = token.get("valueFrom", {}).get("secretKeyRef", {})
        anotar(f"{nombre} · el token viene de Secret Manager", bool(ref.get("name")) and "value" not in token,
               "falta secretKeyRef" if not ref else "")
    sa = spec.get("serviceAccountName", "")
    anotar(f"{nombre} · usa una cuenta de servicio propia", bool(sa) and "compute@" not in sa,
           sa or "usa la cuenta por defecto")
    probe = cont.get("startupProbe", {}).get("httpGet", {})
    anotar(f"{nombre} · tiene startup probe HTTP", bool(probe.get("path")), str(probe) if probe else "")
    anotar(f"{nombre} · sin IDs de proyecto escritos a mano", "${PROJECT_ID}" in texto
           and not re.search(r"projects/[a-z][a-z0-9-]{4,}[0-9]", texto),
           "usa ${PROJECT_ID} como variable")


def main() -> int:
    envs = {BACK / ".env": f"TRADERPULSE_TOKEN={CANARIO}\n", FRONT / ".env.local": f"TRADERPULSE_TOKEN={CANARIO}\n"}
    previos = {p: p.read_text() for p in envs if p.exists()}
    for p, contenido in envs.items():
        p.write_text(contenido)
    try:
        api_ok = construir("api", BACK, IMG_API)
        web_ok = construir("web", FRONT, IMG_WEB)
    finally:
        for p in envs:
            p.unlink(missing_ok=True)
            if p in previos:
                p.write_text(previos[p])

    sh("docker", "network", "create", RED)
    try:
        if not api_ok:
            sin_verificar("api", "api", "sin imagen")
        if not web_ok:
            sin_verificar("web", "web", "sin imagen")
        if api_ok:
            no_root("api", IMG_API)
            sin_secretos_en_imagen("api", IMG_API)
            tamano("api", IMG_API, "api")
            sh("docker", "rm", "-f", "tp-juez-api")
            sh("docker", "run", "-d", "--name", "tp-juez-api", "--network", RED, "-e", "PORT=9091",
               "-e", f"TRADERPULSE_TOKEN={TOKEN}", "-p", "9091:9091", IMG_API)
            estado, _ = esperar_http("http://127.0.0.1:9091/salud")
            anotar("api · escucha en el puerto que dice $PORT", estado == 200, f"HTTP {estado}")
        if web_ok:
            no_root("web", IMG_WEB)
            sin_secretos_en_imagen("web", IMG_WEB)
            tamano("web", IMG_WEB, "web")
            sh("docker", "rm", "-f", "tp-juez-web")
            sh("docker", "run", "-d", "--name", "tp-juez-web", "--network", RED, "-e", "PORT=9092",
               "-e", "API_URL=http://tp-juez-api:9091", "-e", f"TRADERPULSE_TOKEN={TOKEN}",
               "-p", "9092:9092", IMG_WEB)
            estado, html = esperar_http("http://127.0.0.1:9092/?simbolo=NVDA")
            anotar("web · escucha en $PORT y lee API_URL al arrancar", estado == 200
                   and 'data-testid="precio"' in html, f"HTTP {estado}")
            scripts = re.findall(r'src="(/_next/static/[^"]+\.js)"', html)
            filtrado = TOKEN in html
            for s in scripts:
                _, js = esperar_http(f"http://127.0.0.1:9092{s}", 5)
                filtrado = filtrado or TOKEN in js
            anotar("web · el token no llega al navegador", estado == 200 and not filtrado,
                   f"revisados {len(scripts)} scripts" + (" · TOKEN VISIBLE" if filtrado else ""))
            se_detiene_rapido("web", "tp-juez-web")
        if api_ok:
            se_detiene_rapido("api", "tp-juez-api")
    finally:
        sh("docker", "rm", "-f", "tp-juez-api", "tp-juez-web")
        sh("docker", "network", "rm", RED)

    revisar_servicio("api", GCP / "api.servicio.yaml", con_token=True)
    revisar_servicio("web", GCP / "web.servicio.yaml", con_token=True)

    for nombre, ok, detalle in resultados:
        print(f"{'PASA ' if ok else 'FALLA'}  {nombre}" + (f"   ({detalle})" if detalle else ""))
    pasan = sum(ok for _, ok, _ in resultados)
    print(f"\njuez de despliegue: {pasan} de {len(resultados)}")
    return 0 if pasan == len(resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
