from dataclasses import dataclass, field

APROBADA = "aprobada"
FALLIDA = "fallida"
ERROR = "error"


@dataclass
class ResultadoValidacion:
    tabla: str
    expectativa: str
    columna: str | None
    estado: str
    filas_evaluadas: int = 0
    filas_fallidas: int = 0
    detalle: str = ""
    parametros: dict = field(default_factory=dict)
