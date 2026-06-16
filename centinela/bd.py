import os
import time

import psycopg


def conectar(dsn: str | None = None, reintentos: int = 5, espera: float = 2.0):
    dsn = dsn or os.environ["PG_DSN"]
    ultimo_error = None
    for _ in range(reintentos):
        try:
            return psycopg.connect(dsn)
        except psycopg.OperationalError as e:
            ultimo_error = e
            time.sleep(espera)
    raise ultimo_error
