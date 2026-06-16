"""Validadores declarativos de calidad de datos."""

from centinela.modelos import APROBADA, FALLIDA, ResultadoValidacion


def _contar(conexion, sql: str, params: tuple = ()) -> int:
    """Ejecuta una consulta COUNT y devuelve el entero resultante."""
    with conexion.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()[0]


def _resultado(tabla, exp, columna, fallidas, evaluadas, detalle=""):
    """Construye un ResultadoValidacion a partir de los conteos."""
    estado = APROBADA if fallidas == 0 else FALLIDA
    return ResultadoValidacion(
        tabla=tabla,
        expectativa=exp,
        columna=columna,
        estado=estado,
        filas_evaluadas=evaluadas,
        filas_fallidas=fallidas,
        detalle=detalle,
    )


def validar_no_nulo(conexion, tabla: str, exp: dict) -> ResultadoValidacion:
    """Verifica que la columna no tenga valores nulos."""
    col = exp["columna"]
    total = _contar(conexion, f"SELECT count(*) FROM {tabla}")
    nulos = _contar(conexion, f"SELECT count(*) FROM {tabla} WHERE {col} IS NULL")
    return _resultado(tabla, "no_nulo", col, nulos, total, f"{nulos} nulos en {col}")


def validar_unico(conexion, tabla: str, exp: dict) -> ResultadoValidacion:
    """Verifica que los valores de la columna sean únicos."""
    col = exp["columna"]
    total = _contar(conexion, f"SELECT count(*) FROM {tabla}")
    dups = _contar(
        conexion,
        f"SELECT coalesce(sum(c-1), 0) FROM "
        f"(SELECT count(*) c FROM {tabla} GROUP BY {col} HAVING count(*) > 1) t",
    )
    return _resultado(tabla, "unico", col, dups, total, f"{dups} duplicados en {col}")


def validar_rango(conexion, tabla: str, exp: dict) -> ResultadoValidacion:
    """Verifica que los valores estén dentro del rango [min, max]."""
    col, mn, mx = exp["columna"], exp["min"], exp["max"]
    total = _contar(conexion, f"SELECT count(*) FROM {tabla} WHERE {col} IS NOT NULL")
    fuera = _contar(
        conexion,
        f"SELECT count(*) FROM {tabla} WHERE {col} < %s OR {col} > %s",
        (mn, mx),
    )
    return _resultado(tabla, "rango", col, fuera, total, f"{fuera} fuera de [{mn},{mx}]")


def validar_valores_permitidos(conexion, tabla: str, exp: dict) -> ResultadoValidacion:
    """Verifica que los valores de la columna pertenezcan al conjunto permitido."""
    col, permitidos = exp["columna"], list(exp["valores"])
    total = _contar(conexion, f"SELECT count(*) FROM {tabla} WHERE {col} IS NOT NULL")
    fuera = _contar(
        conexion,
        f"SELECT count(*) FROM {tabla} WHERE {col} <> ALL(%s)",
        (permitidos,),
    )
    return _resultado(tabla, "valores_permitidos", col, fuera, total, f"{fuera} no permitidos")


def validar_patron(conexion, tabla: str, exp: dict) -> ResultadoValidacion:
    """Verifica que los valores de la columna cumplan con una expresión regular."""
    col, patron = exp["columna"], exp["patron"]
    total = _contar(conexion, f"SELECT count(*) FROM {tabla} WHERE {col} IS NOT NULL")
    fuera = _contar(
        conexion,
        f"SELECT count(*) FROM {tabla} WHERE {col} !~ %s",
        (patron,),
    )
    return _resultado(tabla, "patron", col, fuera, total, f"{fuera} no cumplen patron")


def validar_frescura(conexion, tabla: str, exp: dict) -> ResultadoValidacion:
    """Verifica que el dato más reciente sea más nuevo que max_horas."""
    col, max_horas = exp["columna"], exp["max_horas"]
    total = _contar(conexion, f"SELECT count(*) FROM {tabla}")
    sql_frescura = (
        f"SELECT CASE WHEN max({col}) < now() - (%s || ' hours')::interval "
        f"THEN 1 ELSE 0 END FROM {tabla}"
    )
    dato_viejo = _contar(conexion, sql_frescura, (max_horas,))
    return _resultado(
        tabla, "frescura", col, dato_viejo, total,
        f"dato mas reciente vs {max_horas}h",
    )


def validar_conteo_filas(conexion, tabla: str, exp: dict) -> ResultadoValidacion:
    """Verifica que el número de filas esté dentro del rango [min, max]."""
    mn, mx = exp["min"], exp["max"]
    total = _contar(conexion, f"SELECT count(*) FROM {tabla}")
    fallida = 0 if mn <= total <= mx else 1
    return _resultado(
        tabla, "conteo_filas", None, fallida, total,
        f"{total} filas (esperado [{mn},{mx}])",
    )


def validar_integridad_referencial(conexion, tabla: str, exp: dict) -> ResultadoValidacion:
    """Verifica que no haya filas huérfanas respecto a la tabla referida."""
    col = exp["columna"]
    ref_tabla, ref_col = exp["tabla_referida"], exp["columna_referida"]
    total = _contar(conexion, f"SELECT count(*) FROM {tabla} WHERE {col} IS NOT NULL")
    huerfanas = _contar(
        conexion,
        f"SELECT count(*) FROM {tabla} t "
        f"LEFT JOIN {ref_tabla} r ON t.{col} = r.{ref_col} "
        f"WHERE t.{col} IS NOT NULL AND r.{ref_col} IS NULL",
    )
    return _resultado(
        tabla, "integridad_referencial", col, huerfanas, total,
        f"{huerfanas} huerfanas",
    )


VALIDADORES = {
    "no_nulo": validar_no_nulo,
    "unico": validar_unico,
    "rango": validar_rango,
    "valores_permitidos": validar_valores_permitidos,
    "patron": validar_patron,
    "frescura": validar_frescura,
    "conteo_filas": validar_conteo_filas,
    "integridad_referencial": validar_integridad_referencial,
}
