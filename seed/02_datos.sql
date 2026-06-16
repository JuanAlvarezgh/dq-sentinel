INSERT INTO dim_pais (id_pais, codigo_iso, nombre, region) VALUES
 (1, 'COL', 'Colombia',        'América Latina'),
 (2, 'BRA', 'Brasil',          'América Latina'),
 (3, 'MEX', 'México',          'América Latina'),
 (4, 'ESP', 'España',          'Europa'),
 (5, 'USA', 'Estados Unidos',  'América del Norte')
ON CONFLICT (id_pais) DO NOTHING;

INSERT INTO dim_indicador (id_indicador, codigo, nombre, unidad) VALUES
 (1, 'PIB_PC',    'PIB per cápita',      'USD'),
 (2, 'INFLACION', 'Inflación anual',     'porcentaje'),
 (3, 'DESEMPLEO', 'Tasa de desempleo',   'porcentaje'),
 (4, 'POBLACION', 'Población total',     'personas')
ON CONFLICT (id_indicador) DO NOTHING;

-- hechos_valor_indicador: 5 paises x 4 indicadores x 3 anios = 60 filas
-- PIB per capita (USD): COL ~6000, BRA ~7500, MEX ~9500, ESP ~27000, USA ~63000
-- Inflacion (%): valores entre 2 y 20
-- Desempleo (%): valores entre 3 y 15
-- Poblacion (personas): millones a cientos de millones

INSERT INTO hechos_valor_indicador (id_pais, id_indicador, anio, valor, cargado_en) VALUES
-- Colombia - PIB per capita
(1, 1, 2021, 5724.38,  now()),
(1, 1, 2022, 6104.11,  now()),
(1, 1, 2023, 6431.87,  now()),
-- Colombia - Inflacion
(1, 2, 2021,  3.51, now()),
(1, 2, 2022, 13.12, now()),
(1, 2, 2023,  9.28, now()),
-- Colombia - Desempleo
(1, 3, 2021, 13.74, now()),
(1, 3, 2022, 11.28, now()),
(1, 3, 2023, 10.20, now()),
-- Colombia - Poblacion
(1, 4, 2021, 51516562, now()),
(1, 4, 2022, 52215503, now()),
(1, 4, 2023, 52886023, now()),

-- Brasil - PIB per capita
(2, 1, 2021, 7507.12,  now()),
(2, 1, 2022, 8917.06,  now()),
(2, 1, 2023, 8994.53,  now()),
-- Brasil - Inflacion
(2, 2, 2021,  8.30, now()),
(2, 2, 2022,  9.28, now()),
(2, 2, 2023,  4.62, now()),
-- Brasil - Desempleo
(2, 3, 2021, 13.20, now()),
(2, 3, 2022,  9.30, now()),
(2, 3, 2023,  7.80, now()),
-- Brasil - Poblacion
(2, 4, 2021, 214326223, now()),
(2, 4, 2022, 215313498, now()),
(2, 4, 2023, 216422446, now()),

-- Mexico - PIB per capita
(3, 1, 2021, 9144.22,  now()),
(3, 1, 2022, 9926.77,  now()),
(3, 1, 2023, 10838.95, now()),
-- Mexico - Inflacion
(3, 2, 2021, 5.69, now()),
(3, 2, 2022, 7.99, now()),
(3, 2, 2023, 5.53, now()),
-- Mexico - Desempleo
(3, 3, 2021, 4.30, now()),
(3, 3, 2022, 3.30, now()),
(3, 3, 2023, 2.80, now()),
-- Mexico - Poblacion
(3, 4, 2021, 126705138, now()),
(3, 4, 2022, 127504125, now()),
(3, 4, 2023, 128455567, now()),

-- España - PIB per capita
(4, 1, 2021, 27056.43, now()),
(4, 1, 2022, 29592.62, now()),
(4, 1, 2023, 30503.18, now()),
-- España - Inflacion
(4, 2, 2021,  3.10, now()),
(4, 2, 2022,  8.40, now()),
(4, 2, 2023,  3.50, now()),
-- España - Desempleo
(4, 3, 2021, 14.80, now()),
(4, 3, 2022, 12.90, now()),
(4, 3, 2023, 11.80, now()),
-- España - Poblacion
(4, 4, 2021, 47415750, now()),
(4, 4, 2022, 47432893, now()),
(4, 4, 2023, 47615034, now()),

-- Estados Unidos - PIB per capita
(5, 1, 2021, 63530.68, now()),
(5, 1, 2022, 65280.04, now()),
(5, 1, 2023, 66139.72, now()),
-- Estados Unidos - Inflacion
(5, 2, 2021, 4.70, now()),
(5, 2, 2022, 8.00, now()),
(5, 2, 2023, 4.12, now()),
-- Estados Unidos - Desempleo
(5, 3, 2021, 5.40, now()),
(5, 3, 2022, 3.61, now()),
(5, 3, 2023, 3.55, now()),
-- Estados Unidos - Poblacion
(5, 4, 2021, 331893745, now()),
(5, 4, 2022, 333287557, now()),
(5, 4, 2023, 334914895, now());
