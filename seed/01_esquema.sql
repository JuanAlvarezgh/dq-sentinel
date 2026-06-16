CREATE TABLE IF NOT EXISTS dim_pais (
    id_pais      INTEGER PRIMARY KEY,
    codigo_iso   TEXT NOT NULL,
    nombre       TEXT NOT NULL,
    region       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_indicador (
    id_indicador INTEGER PRIMARY KEY,
    codigo       TEXT NOT NULL,
    nombre       TEXT NOT NULL,
    unidad       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS hechos_valor_indicador (
    id            BIGSERIAL PRIMARY KEY,
    id_pais       INTEGER NOT NULL,
    id_indicador  INTEGER NOT NULL,
    anio          INTEGER NOT NULL,
    valor         DOUBLE PRECISION,
    cargado_en    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS resultados_validacion (
    id              BIGSERIAL PRIMARY KEY,
    id_corrida      TEXT NOT NULL,
    fecha           TIMESTAMPTZ NOT NULL DEFAULT now(),
    tabla           TEXT NOT NULL,
    expectativa     TEXT NOT NULL,
    columna         TEXT,
    estado          TEXT NOT NULL,
    filas_evaluadas INTEGER NOT NULL DEFAULT 0,
    filas_fallidas  INTEGER NOT NULL DEFAULT 0,
    detalle         TEXT
);
