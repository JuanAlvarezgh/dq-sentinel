"""Motor de ejecucion de suites de validacion sobre contratos YAML."""

import uuid

import yaml

from centinela.modelos import ERROR, ResultadoValidacion
from centinela.validadores import VALIDADORES


def cargar_contrato(ruta: str) -> dict:
    with open(ruta, encoding="utf-8") as f:
        return yaml.safe_load(f)


def ejecutar_suite(conexion, contrato: dict) -> list[ResultadoValidacion]:
    tabla = contrato["tabla"]
    resultados = []
    for exp in contrato["expectativas"]:
        validador = VALIDADORES.get(exp["tipo"])
        if validador is None:
            resultados.append(
                ResultadoValidacion(
                    tabla,
                    exp["tipo"],
                    exp.get("columna"),
                    ERROR,
                    detalle="tipo de expectativa desconocido",
                )
            )
            continue
        try:
            resultados.append(validador(conexion, tabla, exp))
        except Exception as e:  # noqa: BLE001
            resultados.append(
                ResultadoValidacion(
                    tabla,
                    exp["tipo"],
                    exp.get("columna"),
                    ERROR,
                    detalle=str(e),
                )
            )
    return resultados


def nueva_corrida() -> str:
    return uuid.uuid4().hex[:12]


def persistir(conexion, id_corrida: str, resultados: list[ResultadoValidacion]) -> None:
    with conexion.cursor() as cur:
        for r in resultados:
            cur.execute(
                "INSERT INTO resultados_validacion "
                "(id_corrida,tabla,expectativa,columna,estado,"
                "filas_evaluadas,filas_fallidas,detalle) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    id_corrida,
                    r.tabla,
                    r.expectativa,
                    r.columna,
                    r.estado,
                    r.filas_evaluadas,
                    r.filas_fallidas,
                    r.detalle,
                ),
            )
    conexion.commit()
