"""Verifica que el inyector_sucio dispara exactamente los 5 fallos esperados."""
import pytest

from centinela import motor
from centinela.modelos import FALLIDA
from inyector_sucio import inyectar


@pytest.fixture()
def conexion_sucia(conexion):
    """Fixture que parte de datos limpios e inyecta los datos sucios."""
    inyectar(conexion)
    return conexion


def _ejecutar_todos(conexion):
    """Ejecuta las tres suites de contratos y devuelve la lista combinada."""
    rutas = [
        "centinela/contratos/dim_pais.yml",
        "centinela/contratos/dim_indicador.yml",
        "centinela/contratos/hechos_valor_indicador.yml",
    ]
    resultados = []
    for ruta in rutas:
        contrato = motor.cargar_contrato(ruta)
        resultados.extend(motor.ejecutar_suite(conexion, contrato))
    return resultados


def test_al_menos_cinco_fallidas(conexion_sucia):
    resultados = _ejecutar_todos(conexion_sucia)
    fallidas = [r for r in resultados if r.estado == FALLIDA]
    assert len(fallidas) >= 5, (
        f"Se esperaban al menos 5 fallidas, se obtuvieron {len(fallidas)}: "
        + ", ".join(f"{r.tabla}/{r.expectativa}/{r.columna}" for r in fallidas)
    )


def test_falla_no_nulo_valor(conexion_sucia):
    resultados = _ejecutar_todos(conexion_sucia)
    fallo = next(
        (r for r in resultados if r.expectativa == "no_nulo" and r.columna == "valor"),
        None,
    )
    assert fallo is not None, "No se encontro la expectativa no_nulo/valor"
    assert fallo.estado == FALLIDA, f"Se esperaba FALLIDA, se obtuvo {fallo.estado}"


def test_falla_rango_anio(conexion_sucia):
    resultados = _ejecutar_todos(conexion_sucia)
    fallo = next(
        (r for r in resultados if r.expectativa == "rango" and r.columna == "anio"),
        None,
    )
    assert fallo is not None, "No se encontro la expectativa rango/anio"
    assert fallo.estado == FALLIDA, f"Se esperaba FALLIDA, se obtuvo {fallo.estado}"


def test_falla_integridad_referencial_id_pais(conexion_sucia):
    resultados = _ejecutar_todos(conexion_sucia)
    fallo = next(
        (
            r
            for r in resultados
            if r.expectativa == "integridad_referencial" and r.columna == "id_pais"
        ),
        None,
    )
    assert fallo is not None, "No se encontro la expectativa integridad_referencial/id_pais"
    assert fallo.estado == FALLIDA, f"Se esperaba FALLIDA, se obtuvo {fallo.estado}"


def test_falla_valores_permitidos_unidad(conexion_sucia):
    resultados = _ejecutar_todos(conexion_sucia)
    fallo = next(
        (
            r
            for r in resultados
            if r.expectativa == "valores_permitidos" and r.columna == "unidad"
        ),
        None,
    )
    assert fallo is not None, "No se encontro la expectativa valores_permitidos/unidad"
    assert fallo.estado == FALLIDA, f"Se esperaba FALLIDA, se obtuvo {fallo.estado}"


def test_falla_patron_codigo_iso(conexion_sucia):
    resultados = _ejecutar_todos(conexion_sucia)
    fallo = next(
        (
            r
            for r in resultados
            if r.expectativa == "patron" and r.columna == "codigo_iso"
        ),
        None,
    )
    assert fallo is not None, "No se encontro la expectativa patron/codigo_iso"
    assert fallo.estado == FALLIDA, f"Se esperaba FALLIDA, se obtuvo {fallo.estado}"
