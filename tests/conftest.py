import os

import psycopg
import pytest

DSN = os.environ.get("PG_DSN_TEST", "postgresql://centinela:centinela@localhost:5437/calidad")


def _ejecutar_script(cur, ruta: str) -> None:
    """Ejecuta un archivo SQL con multiples sentencias, omitiendo lineas vacias."""
    sql = open(ruta, encoding="utf-8").read()
    for sentencia in sql.split(";"):
        sentencia = sentencia.strip()
        if sentencia:
            cur.execute(sentencia)


@pytest.fixture()
def conexion():
    con = psycopg.connect(DSN)
    con.autocommit = True
    with con.cursor() as cur:
        _ejecutar_script(cur, "seed/01_esquema.sql")
        cur.execute(
            "TRUNCATE hechos_valor_indicador, dim_pais, dim_indicador, "
            "resultados_validacion RESTART IDENTITY CASCADE"
        )
        _ejecutar_script(cur, "seed/02_datos.sql")
    yield con
    con.close()
