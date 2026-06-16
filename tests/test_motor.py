"""Tests del motor de ejecucion de suites de validacion."""

from centinela import motor
from centinela.modelos import APROBADA, ERROR

CONTRATOS = [
    "centinela/contratos/dim_pais.yml",
    "centinela/contratos/dim_indicador.yml",
    "centinela/contratos/hechos_valor_indicador.yml",
]


def test_ejecutar_suite_aprueba(conexion):
    contrato = motor.cargar_contrato("centinela/contratos/dim_pais.yml")
    resultados = motor.ejecutar_suite(conexion, contrato)
    assert all(r.estado == APROBADA for r in resultados)


def test_persistir_resultados(conexion):
    contrato = motor.cargar_contrato("centinela/contratos/dim_pais.yml")
    resultados = motor.ejecutar_suite(conexion, contrato)
    motor.persistir(conexion, "corrida-test", resultados)
    with conexion.cursor() as cur:
        cur.execute("SELECT count(*) FROM resultados_validacion WHERE id_corrida='corrida-test'")
        assert cur.fetchone()[0] == len(resultados)


def test_tipo_desconocido_produce_error(conexion):
    contrato = {
        "tabla": "dim_pais",
        "expectativas": [
            {"tipo": "expectativa_inexistente", "columna": "id_pais"},
        ],
    }
    resultados = motor.ejecutar_suite(conexion, contrato)
    assert len(resultados) == 1
    assert resultados[0].estado == ERROR
    assert "desconocido" in resultados[0].detalle


def test_tres_contratos_todos_aprueban(conexion):
    fallidas = []
    conteos = {}
    for ruta in CONTRATOS:
        contrato = motor.cargar_contrato(ruta)
        resultados = motor.ejecutar_suite(conexion, contrato)
        conteos[contrato["tabla"]] = len(resultados)
        for r in resultados:
            if r.estado != APROBADA:
                fallidas.append((contrato["tabla"], r.expectativa, r.columna, r.estado, r.detalle))
    assert fallidas == [], f"Expectativas fallidas o con error: {fallidas}"
