"""Corre todas las suites: valida, persiste, genera reporte y alerta si hay fallos."""
import glob

from centinela import motor, notificador, reporte
from centinela.bd import conectar
from centinela.modelos import FALLIDA


def main():
    con = conectar()
    id_corrida = motor.nueva_corrida()
    todos = []
    for ruta in sorted(glob.glob("centinela/contratos/*.yml")):
        contrato = motor.cargar_contrato(ruta)
        todos.extend(motor.ejecutar_suite(con, contrato))
    motor.persistir(con, id_corrida, todos)
    reporte.guardar(reporte.render(todos))
    fallidos = [r for r in todos if r.estado == FALLIDA]
    if fallidos:
        notificador.enviar_alerta(fallidos)
    print(f"Corrida {id_corrida}: {len(todos)} validaciones, {len(fallidos)} fallidas.")
    return 1 if fallidos else 0


if __name__ == "__main__":
    raise SystemExit(main())
