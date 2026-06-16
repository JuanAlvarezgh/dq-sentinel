"""Prueba de humo: verifica que el fixture de conexion y el seed funcionan."""


def test_conexion_basica(conexion):
    with conexion.cursor() as cur:
        cur.execute("SELECT 1")
        resultado = cur.fetchone()
    assert resultado == (1,)


def test_seed_paises(conexion):
    with conexion.cursor() as cur:
        cur.execute("SELECT count(*) FROM dim_pais")
        (total,) = cur.fetchone()
    assert total == 5


def test_seed_indicadores(conexion):
    with conexion.cursor() as cur:
        cur.execute("SELECT count(*) FROM dim_indicador")
        (total,) = cur.fetchone()
    assert total == 4


def test_seed_hechos(conexion):
    with conexion.cursor() as cur:
        cur.execute("SELECT count(*) FROM hechos_valor_indicador")
        (total,) = cur.fetchone()
    assert total == 60
