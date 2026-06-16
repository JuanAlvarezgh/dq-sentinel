"""Tests para los validadores declarativos de calidad de datos."""

import centinela.validadores as v
from centinela.modelos import APROBADA, FALLIDA

# ---------------------------------------------------------------------------
# no_nulo
# ---------------------------------------------------------------------------

def test_no_nulo_aprueba(conexion):
    r = v.validar_no_nulo(conexion, "dim_pais", {"columna": "nombre"})
    assert r.estado == APROBADA


def test_no_nulo_falla(conexion):
    with conexion.cursor() as cur:
        cur.execute(
            "INSERT INTO hechos_valor_indicador (id_pais, id_indicador, anio, valor) "
            "VALUES (1, 1, 2020, NULL)"
        )
    r = v.validar_no_nulo(conexion, "hechos_valor_indicador", {"columna": "valor"})
    assert r.estado == FALLIDA
    assert r.filas_fallidas == 1


# ---------------------------------------------------------------------------
# unico
# ---------------------------------------------------------------------------

def test_unico_aprueba(conexion):
    r = v.validar_unico(conexion, "dim_pais", {"columna": "id_pais"})
    assert r.estado == APROBADA


def test_unico_falla(conexion):
    with conexion.cursor() as cur:
        # id_pais es INTEGER PRIMARY KEY (no serial), se provee explicitamente
        cur.execute(
            "INSERT INTO dim_pais (id_pais, codigo_iso, nombre, region) "
            "VALUES (99, 'COL', 'Duplicado', 'America Latina')"
        )
    r = v.validar_unico(conexion, "dim_pais", {"columna": "codigo_iso"})
    assert r.estado == FALLIDA
    assert r.filas_fallidas >= 1


# ---------------------------------------------------------------------------
# rango
# ---------------------------------------------------------------------------

def test_rango_aprueba(conexion):
    exp = {"columna": "anio", "min": 1960, "max": 2025}
    r = v.validar_rango(conexion, "hechos_valor_indicador", exp)
    assert r.estado == APROBADA


def test_rango_falla(conexion):
    with conexion.cursor() as cur:
        cur.execute(
            "INSERT INTO hechos_valor_indicador (id_pais, id_indicador, anio, valor) "
            "VALUES (1, 1, 3050, 999.99)"
        )
    exp = {"columna": "anio", "min": 1960, "max": 2025}
    r = v.validar_rango(conexion, "hechos_valor_indicador", exp)
    assert r.estado == FALLIDA
    assert r.filas_fallidas == 1


# ---------------------------------------------------------------------------
# valores_permitidos
# ---------------------------------------------------------------------------

def test_valores_permitidos_aprueba(conexion):
    r = v.validar_valores_permitidos(
        conexion,
        "dim_indicador",
        {"columna": "unidad", "valores": ["USD", "porcentaje", "personas"]},
    )
    assert r.estado == APROBADA


def test_valores_permitidos_falla(conexion):
    with conexion.cursor() as cur:
        # id_indicador es INTEGER PRIMARY KEY (no serial), se provee explicitamente
        cur.execute(
            "INSERT INTO dim_indicador (id_indicador, codigo, nombre, unidad) "
            "VALUES (99, 'PESO', 'Peso promedio', 'kg')"
        )
    r = v.validar_valores_permitidos(
        conexion,
        "dim_indicador",
        {"columna": "unidad", "valores": ["USD", "porcentaje", "personas"]},
    )
    assert r.estado == FALLIDA
    assert r.filas_fallidas == 1


# ---------------------------------------------------------------------------
# patron
# ---------------------------------------------------------------------------

def test_patron_aprueba(conexion):
    exp_patron = {"columna": "codigo_iso", "patron": "^[A-Z]{3}$"}
    r = v.validar_patron(conexion, "dim_pais", exp_patron)
    assert r.estado == APROBADA


def test_patron_falla(conexion):
    with conexion.cursor() as cur:
        # id_pais es INTEGER PRIMARY KEY (no serial), se provee explicitamente
        cur.execute(
            "INSERT INTO dim_pais (id_pais, codigo_iso, nombre, region) "
            "VALUES (99, 'co', 'minuscula', 'America Latina')"
        )
    exp_patron = {"columna": "codigo_iso", "patron": "^[A-Z]{3}$"}
    r = v.validar_patron(conexion, "dim_pais", exp_patron)
    assert r.estado == FALLIDA
    assert r.filas_fallidas == 1


# ---------------------------------------------------------------------------
# frescura
# ---------------------------------------------------------------------------

def test_frescura_aprueba(conexion):
    r = v.validar_frescura(
        conexion,
        "hechos_valor_indicador",
        {"columna": "cargado_en", "max_horas": 48},
    )
    assert r.estado == APROBADA


def test_frescura_falla(conexion):
    with conexion.cursor() as cur:
        cur.execute(
            "UPDATE hechos_valor_indicador SET cargado_en = now() - interval '10 days'"
        )
    r = v.validar_frescura(
        conexion,
        "hechos_valor_indicador",
        {"columna": "cargado_en", "max_horas": 48},
    )
    assert r.estado == FALLIDA


# ---------------------------------------------------------------------------
# conteo_filas
# ---------------------------------------------------------------------------

def test_conteo_filas_aprueba(conexion):
    r = v.validar_conteo_filas(
        conexion,
        "hechos_valor_indicador",
        {"min": 1, "max": 100000},
    )
    assert r.estado == APROBADA


def test_conteo_filas_falla(conexion):
    # hay 60 filas; el rango [1000, 2000] no las incluye
    r = v.validar_conteo_filas(
        conexion,
        "hechos_valor_indicador",
        {"min": 1000, "max": 2000},
    )
    assert r.estado == FALLIDA


# ---------------------------------------------------------------------------
# integridad_referencial
# ---------------------------------------------------------------------------

def test_integridad_referencial_aprueba(conexion):
    r = v.validar_integridad_referencial(
        conexion,
        "hechos_valor_indicador",
        {"columna": "id_pais", "tabla_referida": "dim_pais", "columna_referida": "id_pais"},
    )
    assert r.estado == APROBADA


def test_integridad_referencial_falla(conexion):
    with conexion.cursor() as cur:
        # El esquema no declara FK, asi que id_pais=999 (inexistente en dim_pais)
        # entra sin problema y el validador lo detecta como huerfana via LEFT JOIN.
        cur.execute(
            "INSERT INTO hechos_valor_indicador (id_pais, id_indicador, anio, valor) "
            "VALUES (999, 1, 2021, 100.0)"
        )
    r = v.validar_integridad_referencial(
        conexion,
        "hechos_valor_indicador",
        {"columna": "id_pais", "tabla_referida": "dim_pais", "columna_referida": "id_pais"},
    )
    assert r.estado == FALLIDA
    assert r.filas_fallidas == 1
