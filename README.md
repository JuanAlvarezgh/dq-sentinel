# dq-sentinel

Framework de calidad de datos y observabilidad sobre un warehouse PostgreSQL con reglas declarativas en YAML, reporte HTML y alertas a Slack.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-2.10-017CEE?logo=apache-airflow&logoColor=white)](https://airflow.apache.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![pytest](https://img.shields.io/badge/pytest-36%20tests-0A9EDC?logo=pytest&logoColor=white)](https://pytest.org/)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)

---

## Resumen

`dq-sentinel` es un framework propio de calidad de datos construido desde cero sobre Python y PostgreSQL. Valida un warehouse dimensional con contratos declarativos en YAML, persiste el histórico de resultados para observabilidad, genera un reporte HTML por corrida y envía alertas a Slack cuando alguna expectativa falla.

El proyecto resuelve un problema concreto del día a día en ingeniería de datos: garantizar que los datos que alimentan modelos de análisis y reportes cumplan con invariantes definidas (nulidad, unicidad, rangos, patrones, integridad referencial, frescura y conteo de filas) antes de que los errores lleguen a producción.

---

## Por qué este proyecto

La observabilidad de datos es uno de los diferenciadores más claros entre un ingeniero junior y uno senior. Detectar un valor fuera de rango o una fila huérfana en cuanto llega al warehouse, antes de que contamine tableros o modelos, requiere infraestructura dedicada.

Herramientas como Great Expectations o Soda resuelven este problema pero agregan dependencias pesadas y curvas de adopción largas. `dq-sentinel` demuestra que la misma lógica puede implementarse con código minimalista, legible y completamente controlado por el equipo.

El uso de **data contracts** en YAML separa la definición de las reglas del código que las evalúa. Cualquier miembro del equipo puede agregar o modificar una expectativa sin tocar Python, y el motor la recoge automáticamente en la siguiente corrida.

---

## Arquitectura

```mermaid
flowchart TD
    seed["seed/*.sql<br/>(datos iniciales)"]
    inyector["inyector_sucio.py<br/>(demo de fallos)"]
    pg[("PostgreSQL<br/>dim_pais / dim_indicador<br/>hechos_valor_indicador")]
    contratos["contratos YAML<br/>centinela/contratos/*.yml"]
    motor["motor.py<br/>(ejecuta expectativas)"]
    resultados[("resultados_validacion<br/>(histórico / observabilidad)")]
    reporte["reporte HTML<br/>salida/reporte.html"]
    slack["Alerta Slack<br/>(si hay fallos)"]
    airflow["Apache Airflow<br/>DAG: centinela_calidad<br/>@hourly"]

    seed --> pg
    inyector --> pg
    contratos --> motor
    pg --> motor
    motor --> resultados
    motor --> reporte
    motor --> slack
    airflow -. orquesta .-> motor
```

El flujo principal se inicia con `ejecutar.py`, que carga todos los contratos YAML, evalúa cada expectativa contra el warehouse, persiste los resultados en `resultados_validacion` y genera el reporte. Airflow puede orquestar este flujo de forma programada sin cambiar ninguna línea del motor.

---

## Tipos de expectativa

| Tipo                    | Descripción                                                                 |
|-------------------------|-----------------------------------------------------------------------------|
| `no_nulo`               | Verifica que la columna no contenga valores nulos.                          |
| `unico`                 | Verifica que los valores de la columna sean únicos (sin duplicados).        |
| `rango`                 | Verifica que los valores numéricos estén dentro del intervalo [min, max].   |
| `valores_permitidos`    | Verifica que los valores pertenezcan a un conjunto discreto predefinido.    |
| `patron`                | Verifica que los valores de texto cumplan una expresión regular.            |
| `frescura`              | Verifica que el registro más reciente sea más nuevo que un umbral en horas. |
| `conteo_filas`          | Verifica que el número de filas en la tabla esté dentro de [min, max].      |
| `integridad_referencial`| Verifica que no existan filas huérfanas respecto a una tabla referenciada.  |

---

## Data contracts

Cada tabla tiene un contrato en `centinela/contratos/<tabla>.yml`. El motor lee todos los contratos al inicio de cada corrida y ejecuta las expectativas en orden. El formato es intencional: simple, autodocumentado y versionable en git.

Ejemplo del contrato más completo, `hechos_valor_indicador.yml`:

```yaml
tabla: hechos_valor_indicador
descripcion: Hechos de valores de indicadores por país y año.
expectativas:
  - tipo: no_nulo
    columna: valor
  - tipo: rango
    columna: anio
    min: 1960
    max: 2025
  - tipo: integridad_referencial
    columna: id_pais
    tabla_referida: dim_pais
    columna_referida: id_pais
  - tipo: integridad_referencial
    columna: id_indicador
    tabla_referida: dim_indicador
    columna_referida: id_indicador
  - tipo: frescura
    columna: cargado_en
    max_horas: 48
  - tipo: conteo_filas
    min: 1
    max: 100000
```

El motor resuelve el tipo de expectativa a través de un registro `VALIDADORES` y despacha la función correspondiente. Si el tipo no existe, el resultado se registra como `error` sin detener el resto de la corrida.

---

## Cómo ejecutarlo

### Requisitos

- Docker Desktop con Compose V2.
- (Opcional) Variable de entorno `SLACK_WEBHOOK_URL` para recibir alertas en Slack.

### Demostración rápida

```bash
# 1. Levantar Postgres e inicializar el warehouse con los datos de semilla
docker compose up -d postgres

# 2. (En otra terminal) Ejecutar todas las validaciones sobre datos limpios
PG_DSN=postgresql://centinela:centinela@localhost:5437/calidad python ejecutar.py
# Salida: Corrida <id>: 12 validaciones, 0 fallidas.

# 3. Inyectar datos sucios
PG_DSN=postgresql://centinela:centinela@localhost:5437/calidad python inyector_sucio.py

# 4. Volver a ejecutar las validaciones
PG_DSN=postgresql://centinela:centinela@localhost:5437/calidad python ejecutar.py
# Salida: Corrida <id>: 12 validaciones, 5 fallidas.
# El reporte HTML queda en salida/reporte.html
```

### Con Docker Compose completo

```bash
# Ejecuta el servicio centinela (validaciones) una sola vez contra Postgres
docker compose up
```

### Alerta a Slack

```bash
# Exportar el webhook antes de correr el CLI o docker compose
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

Si la variable no está definida, la alerta se imprime en consola en lugar de enviarse a Slack.

### Airflow (opcional)

```bash
# Levantar Postgres + Airflow (perfil adicional, puede tardar ~60s)
docker compose --profile airflow up

# Acceder a la interfaz web
# http://localhost:8080  (usuario: admin, contraseña generada en el primer arranque)
```

El DAG `centinela_calidad` ejecuta `ejecutar.py` con frecuencia `@hourly`. No requiere modificar el motor ni los contratos.

### Generar los gráficos

```bash
PG_DSN=postgresql://centinela:centinela@localhost:5437/calidad python analisis/graficos.py
# Guarda docs/img/resultados_por_tabla.png y docs/img/resumen_corrida.png
```

---

## Resultados e interpretación

### Corrida sobre datos limpios

| Métrica               | Valor |
|-----------------------|-------|
| Contratos evaluados   | 3     |
| Expectativas totales  | 12    |
| Aprobadas             | 12    |
| Fallidas              | 0     |
| Código de salida      | 0     |

Todas las expectativas pasan. El warehouse refleja el estado esperado: sin nulos en columnas críticas, códigos ISO en formato correcto, rangos de año válidos, integridad referencial intacta.

### Corrida tras inyectar datos sucios

| Métrica               | Valor |
|-----------------------|-------|
| Contratos evaluados   | 3     |
| Expectativas totales  | 12    |
| Aprobadas             | 7     |
| Fallidas              | 5     |
| Código de salida      | 1     |

Los 5 fallos detectados y su interpretación:

| Tabla                       | Columna     | Tipo                    | Filas fallidas | Detalle                                          |
|-----------------------------|-------------|-------------------------|----------------|--------------------------------------------------|
| `dim_indicador`             | `unidad`    | `valores_permitidos`    | 1              | Valor `kg` no pertenece al catálogo `[USD, porcentaje, personas]`. Indica un indicador cargado con unidad incorrecta; cualquier agregación monetaria o porcentual sobre este dato produciría resultados sin sentido. |
| `dim_pais`                  | `codigo_iso`| `patron`                | 1              | Valor `co` no cumple la expresión `^[A-Z]{3}$`. El estándar ISO 3166-1 alpha-3 exige tres letras mayúsculas. Un código en minúscula rompe los cruces con fuentes externas. |
| `hechos_valor_indicador`    | `valor`     | `no_nulo`               | 1              | Fila con `valor = NULL`. Un hecho sin valor numérico es inutilizable en cálculos de promedio o suma. |
| `hechos_valor_indicador`    | `anio`      | `rango`                 | 1              | Valor `3050` fuera del rango `[1960, 2025]`. Dato de año evidentemente erróneo, probablemente por un error de tecleo. Corrompería las visualizaciones de series temporales. |
| `hechos_valor_indicador`    | `id_pais`   | `integridad_referencial`| 1              | `id_pais = 999` no existe en `dim_pais`. Fila huérfana: el hecho no puede resolverse a un país conocido. En un modelo dimensional esto produce NULL silenciosos en los reportes. |

### Gráficos

**Resultados por tabla — corrida con datos sucios**

![Resultados por tabla](docs/img/resultados_por_tabla.png)

La barra de `hechos_valor_indicador` muestra 3 expectativas fallidas de 6, la de `dim_pais` 1 de 4 y la de `dim_indicador` 1 de 2. Las dimensiones tienen menor exposición porque sus contratos son más simples; la tabla de hechos concentra la mayoría de las reglas de negocio.

**Resumen de corrida**

![Resumen de corrida](docs/img/resumen_corrida.png)

58 % de expectativas aprobadas y 42 % fallidas en la corrida con datos sucios. En producción este porcentaje debería mantenerse en 100 % aprobadas; cualquier desviación genera alerta.

### Observabilidad con resultados_validacion

Cada corrida persiste sus resultados en la tabla `resultados_validacion` con un identificador único (`id_corrida`), la fecha exacta, la tabla, el tipo de expectativa, el estado y el conteo de filas fallidas. Esto permite:

- Auditar el historial de calidad por tabla a lo largo del tiempo.
- Detectar degradación progresiva (por ejemplo, un porcentaje de nulos que crece semana a semana).
- Correlacionar fallos con ventanas de carga específicas.
- Construir tableros de SLA sobre los propios datos de validación.

---

## Pruebas y calidad

```
pytest tests -v
```

- **36 pruebas** cubren: conexión al warehouse, semilla de datos, los 8 validadores (escenario aprobado y fallido por tipo), motor de ejecución y persistencia, notificador de Slack (con mock HTTP), renderizado del reporte HTML y corrida de integración con el inyector de datos sucios.
- **1 prueba omitida**: `test_dag.py` requiere Apache Airflow en el entorno de ejecución. Se omite automáticamente con `pytest.importorskip` cuando Airflow no está instalado, de modo que el CI no se bloquea (el DAG corre de verdad dentro del contenedor de Airflow).
- **ruff** verifica estilo y ordenamiento de imports en todo el proyecto (`E`, `F`, `I`, `UP`, `B`).
- **CI en GitHub Actions**: cada push ejecuta `pytest` y `ruff check` contra un servicio PostgreSQL 16 real.

---

## Estructura del proyecto

```
dq-sentinel/
 centinela/
   contratos/         # Data contracts YAML (uno por tabla)
   plantillas/        # Plantilla Jinja2 del reporte HTML
   bd.py              # Conexión a Postgres con reintentos
   modelos.py         # Dataclass ResultadoValidacion
   motor.py           # Carga contratos, ejecuta suites, persiste resultados
   validadores.py     # Implementación de los 8 tipos de expectativa
   reporte.py         # Renderizado del reporte HTML
   notificador.py     # Envío de alertas a Slack
 analisis/
   graficos.py        # Genera PNG de resultados desde resultados_validacion
 dags/
   centinela_calidad.py  # DAG de Airflow (@hourly)
 docs/
   img/               # Gráficos PNG generados
 seed/
   01_esquema.sql     # DDL del warehouse
   02_datos.sql       # Datos de semilla
 tests/               # Suite de pruebas pytest
 ejecutar.py          # CLI principal
 inyector_sucio.py    # Inyector de datos erróneos (demostración)
 docker-compose.yml   # Infraestructura (Postgres + centinela + Airflow opcional)
 pyproject.toml       # Configuración del proyecto, ruff y pytest
```

---

## Limitaciones

- Las validaciones operan a nivel de tabla y columna. No incluyen perfilado estadístico avanzado (distribución, curtosis, valores atípicos multivariados) ni detección de anomalías con modelos de aprendizaje automático.
- El contrato YAML no incluye todavía soporte para expresiones SQL arbitrarias como expectativas personalizadas.
- Airflow se incluye como perfil de Docker opcional para la demostración. En un entorno de producción requeriría configuración adicional (base de datos de metadatos propia, usuarios, autenticación).
- El reporte HTML no es interactivo; es una instantánea por corrida. La observabilidad a largo plazo depende de consultar directamente `resultados_validacion` o de construir una capa de visualización sobre ella.

---

## Contacto

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/juanalvarezgh)
[![Gmail](https://img.shields.io/badge/Gmail-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:juanalvarezghcode@gmail.com)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/JuanAlvarezgh)
