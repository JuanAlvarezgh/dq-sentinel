from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from centinela.modelos import APROBADA, ERROR, FALLIDA

_PLANTILLAS = Path(__file__).parent / "plantillas"


def render(resultados, historico=None) -> str:
    env = Environment(loader=FileSystemLoader(str(_PLANTILLAS)), autoescape=True)
    plantilla = env.get_template("reporte.html.j2")
    return plantilla.render(
        resultados=resultados,
        historico=historico or [],
        aprobadas=sum(r.estado == APROBADA for r in resultados),
        fallidas=sum(r.estado == FALLIDA for r in resultados),
        errores=sum(r.estado == ERROR for r in resultados),
    )


def guardar(html: str, ruta: str = "salida/reporte.html") -> str:
    p = Path(ruta)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html, encoding="utf-8")
    return str(p)
