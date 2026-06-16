"""Genera graficos de resultados de validacion a partir de la tabla resultados_validacion."""

import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mpatches  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

from centinela.bd import conectar

DIRECTORIO_IMG = Path(__file__).parent.parent / "docs" / "img"
COLOR_APROBADA = "#2ecc71"
COLOR_FALLIDA = "#e74c3c"


def _obtener_ultima_corrida(conexion):
    """Retorna el id_corrida mas reciente registrado en resultados_validacion."""
    with conexion.cursor() as cur:
        cur.execute(
            "SELECT id_corrida FROM resultados_validacion "
            "ORDER BY fecha DESC LIMIT 1"
        )
        fila = cur.fetchone()
        if fila is None:
            raise RuntimeError("No hay corridas registradas en resultados_validacion.")
        return fila[0]


def _leer_resultados(conexion, id_corrida: str) -> list[dict]:
    """Lee los resultados de una corrida especifica."""
    with conexion.cursor() as cur:
        cur.execute(
            "SELECT tabla, estado, COUNT(*) as total "
            "FROM resultados_validacion "
            "WHERE id_corrida = %s "
            "GROUP BY tabla, estado "
            "ORDER BY tabla, estado",
            (id_corrida,),
        )
        filas = cur.fetchall()
    return [{"tabla": f[0], "estado": f[1], "total": f[2]} for f in filas]


def grafico_resultados_por_tabla(conexion, id_corrida: str | None = None) -> Path:
    """
    Genera un grafico de barras apiladas: expectativas aprobadas vs fallidas por tabla.
    Guarda el PNG en docs/img/resultados_por_tabla.png.
    """
    id_corrida = id_corrida or _obtener_ultima_corrida(conexion)
    filas = _leer_resultados(conexion, id_corrida)

    # Agregar por tabla
    tablas_datos: dict[str, dict[str, int]] = {}
    for fila in filas:
        tabla = fila["tabla"]
        if tabla not in tablas_datos:
            tablas_datos[tabla] = {"aprobada": 0, "fallida": 0, "error": 0}
        estado = fila["estado"]
        if estado in tablas_datos[tabla]:
            tablas_datos[tabla][estado] = fila["total"]

    tablas = list(tablas_datos.keys())
    aprobadas = [tablas_datos[t]["aprobada"] for t in tablas]
    fallidas = [tablas_datos[t]["fallida"] for t in tablas]

    # Etiquetas mas cortas para visualizacion
    etiquetas = [t.replace("hechos_valor_indicador", "hechos_valor_ind.") for t in tablas]

    x = range(len(tablas))
    ancho = 0.55

    fig, ax = plt.subplots(figsize=(9, 5))
    barras_aprobadas = ax.bar(x, aprobadas, ancho, label="Aprobadas", color=COLOR_APROBADA)
    barras_fallidas = ax.bar(
        x, fallidas, ancho, bottom=aprobadas, label="Fallidas", color=COLOR_FALLIDA
    )

    # Anotaciones de valor dentro de cada segmento
    for barra, valor in zip(barras_aprobadas, aprobadas, strict=False):
        if valor > 0:
            ax.text(
                barra.get_x() + barra.get_width() / 2,
                barra.get_height() / 2,
                str(valor),
                ha="center",
                va="center",
                fontsize=10,
                fontweight="bold",
                color="white",
            )
    for barra, base, valor in zip(barras_fallidas, aprobadas, fallidas, strict=False):
        if valor > 0:
            ax.text(
                barra.get_x() + barra.get_width() / 2,
                base + valor / 2,
                str(valor),
                ha="center",
                va="center",
                fontsize=10,
                fontweight="bold",
                color="white",
            )

    ax.set_xticks(list(x))
    ax.set_xticklabels(etiquetas, fontsize=10)
    ax.set_ylabel("Número de expectativas", fontsize=11)
    ax.set_title(
        f"Resultados por tabla — corrida con datos sucios (id: {id_corrida})",
        fontsize=13,
        pad=14,
    )
    ax.set_ylim(0, max(a + f for a, f in zip(aprobadas, fallidas, strict=False)) + 1.5)
    ax.legend(fontsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    DIRECTORIO_IMG.mkdir(parents=True, exist_ok=True)
    ruta = DIRECTORIO_IMG / "resultados_por_tabla.png"
    fig.tight_layout()
    fig.savefig(ruta, dpi=150)
    plt.close(fig)
    print(f"Guardado: {ruta}")
    return ruta


def grafico_resumen_corrida(conexion, id_corrida: str | None = None) -> Path:
    """
    Genera un grafico de dona con el total de expectativas aprobadas vs fallidas.
    Guarda el PNG en docs/img/resumen_corrida.png.
    """
    id_corrida = id_corrida or _obtener_ultima_corrida(conexion)

    with conexion.cursor() as cur:
        cur.execute(
            "SELECT estado, COUNT(*) FROM resultados_validacion "
            "WHERE id_corrida = %s GROUP BY estado",
            (id_corrida,),
        )
        conteos = {fila[0]: fila[1] for fila in cur.fetchall()}

    aprobadas = conteos.get("aprobada", 0)
    fallidas = conteos.get("fallida", 0)
    total = aprobadas + fallidas

    fig, ax = plt.subplots(figsize=(6, 5))
    valores = [aprobadas, fallidas]
    colores = [COLOR_APROBADA, COLOR_FALLIDA]
    etiquetas = [f"Aprobadas ({aprobadas})", f"Fallidas ({fallidas})"]

    wedges, texts, autotexts = ax.pie(
        valores,
        labels=None,
        colors=colores,
        autopct="%1.0f%%",
        startangle=90,
        wedgeprops={"width": 0.55},
        pctdistance=0.75,
    )
    for at in autotexts:
        at.set_fontsize(12)
        at.set_fontweight("bold")
        at.set_color("white")

    parches = [
        mpatches.Patch(color=colores[i], label=etiquetas[i]) for i in range(len(etiquetas))
    ]
    ax.legend(handles=parches, loc="lower center", bbox_to_anchor=(0.5, -0.08), fontsize=10)
    ax.set_title(
        f"Resumen de corrida — {total} expectativas evaluadas",
        fontsize=13,
        pad=14,
    )

    DIRECTORIO_IMG.mkdir(parents=True, exist_ok=True)
    ruta = DIRECTORIO_IMG / "resumen_corrida.png"
    fig.tight_layout()
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Guardado: {ruta}")
    return ruta


if __name__ == "__main__":
    dsn = os.environ.get("PG_DSN")
    if not dsn:
        raise SystemExit("Variable PG_DSN no definida.")
    con = conectar(dsn)
    grafico_resultados_por_tabla(con)
    grafico_resumen_corrida(con)
    con.close()
