"""Introduce datos sucios para demostrar la deteccion de fallos."""
from centinela.bd import conectar


def inyectar(conexion):
    with conexion.cursor() as cur:
        # no_nulo: valor NULL en hechos_valor_indicador
        cur.execute(
            "INSERT INTO hechos_valor_indicador (id_pais, id_indicador, anio, valor)"
            " VALUES (1, 1, 2023, NULL)"
        )
        # rango: anio fuera del rango [1960, 2025]
        cur.execute(
            "INSERT INTO hechos_valor_indicador (id_pais, id_indicador, anio, valor)"
            " VALUES (1, 1, 3050, 5.0)"
        )
        # integridad_referencial: id_pais 999 no existe en dim_pais
        cur.execute(
            "INSERT INTO hechos_valor_indicador (id_pais, id_indicador, anio, valor)"
            " VALUES (999, 1, 2023, 5.0)"
        )
        # valores_permitidos: unidad 'kg' no esta en [USD, porcentaje, personas]
        cur.execute(
            "INSERT INTO dim_indicador (id_indicador, codigo, nombre, unidad)"
            " VALUES (99, 'PESO', 'Peso promedio', 'kg')"
        )
        # patron: codigo_iso 'co' no cumple ^[A-Z]{3}$
        cur.execute(
            "INSERT INTO dim_pais (id_pais, codigo_iso, nombre, region)"
            " VALUES (99, 'co', 'Pais minuscula', 'X')"
        )
    conexion.commit()


if __name__ == "__main__":
    con = conectar()
    inyectar(con)
    print("Datos sucios inyectados.")
