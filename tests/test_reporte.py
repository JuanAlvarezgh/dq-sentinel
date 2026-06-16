from centinela import reporte
from centinela.modelos import APROBADA, FALLIDA, ResultadoValidacion

RES = [
    ResultadoValidacion("dim_pais", "unico", "id_pais", APROBADA, 5, 0, "ok"),
    ResultadoValidacion("hechos_valor_indicador", "no_nulo", "valor", FALLIDA, 40, 2, "2 nulos"),
]


def test_render_contiene_resumen():
    html = reporte.render(RES, historico=[])
    assert "dim_pais" in html
    assert "2 nulos" in html
    assert "fallida" in html


def test_render_con_historico():
    historico = [{"id_corrida": "abc123", "aprobadas": 10, "fallidas": 2}]
    html = reporte.render(RES, historico=historico)
    assert "abc123" in html


def test_guardar_escribe_archivo(tmp_path):
    html = reporte.render(RES)
    ruta_salida = str(tmp_path / "reporte_prueba.html")
    ruta_devuelta = reporte.guardar(html, ruta=ruta_salida)
    archivo = tmp_path / "reporte_prueba.html"
    assert archivo.exists()
    contenido = archivo.read_text(encoding="utf-8")
    assert "dim_pais" in contenido
    assert ruta_devuelta == ruta_salida
