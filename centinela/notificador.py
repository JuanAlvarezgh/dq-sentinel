import os

import httpx


def construir_mensaje(fallidos) -> str:
    lineas = [f":rotating_light: {len(fallidos)} validaciones fallidas en el warehouse:"]
    for r in fallidos:
        lineas.append(
            f"• {r.tabla}.{r.columna or '-'} [{r.expectativa}]"
            f" — {r.filas_fallidas} filas: {r.detalle}"
        )
    return "\n".join(lineas)


def enviar_alerta(fallidos, webhook_url: str | None = None) -> bool:
    webhook = webhook_url or os.environ.get("SLACK_WEBHOOK_URL")
    mensaje = construir_mensaje(fallidos)
    if not webhook:
        print(f"[ALERTA-CONSOLA] {mensaje}")
        return False
    resp = httpx.post(webhook, json={"text": mensaje}, timeout=10)
    resp.raise_for_status()
    return True
