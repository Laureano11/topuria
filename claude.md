# Contexto del proyecto `topuria`

## Objetivo funcional

Aplicación web personal para trackear hábitos y objetivos, con:

- Marcado de cumplimiento por día.
- Vistas agregadas por semana, mes y año.
- Soporte para hábitos de tipo:
  - `positive`: marcar cuando se cumple.
  - `avoid`: marcar cuando se falla (sirve para racha de abstinencia).
- Gestión de hábitos: crear, editar y eliminar.

La app está pensada para un único usuario (uso personal), con persistencia en servidor para sincronización automática.

---

## Stack tecnológico

- **Backend:** FastAPI
- **Persistencia:** SQLite
- **ORM/modelado:** SQLModel
- **UI server-side:** Jinja2 templates
- **Interacción parcial:** HTMX
- **Deploy:** Fly.io
- **Persistencia cloud:** volumen montado en Fly (`/data/sqlite.db`)

Dependencias principales en `requirements.txt`:

- `fastapi`
- `uvicorn[standard]`
- `sqlmodel`
- `jinja2`
- `python-multipart`

---

## Arquitectura (alto nivel)

1. El navegador renderiza HTML desde FastAPI (Jinja2).
2. Los checks se actualizan con HTMX (`POST /checks/set`) sin recargar toda la página.
3. Los datos se guardan en SQLite (`SQLModel`) en volumen persistente.
4. Las vistas semana/mes/año calculan agregaciones desde `HabitCheck`.

---

## Estructura de carpetas

- `app/main.py`: inicializa FastAPI, rutas, templates, static y startup DB.
- `app/db.py`: engine, sesiones e inicialización/migración ligera de columnas SQLite.
- `app/models.py`: modelos `Habit` y `HabitCheck`.
- `app/dates.py`: utilidades de fecha/hora y zona horaria local.
- `app/routes/views.py`: vistas `/day`, `/week`, `/month`, `/year`.
- `app/routes/habits.py`: crear/editar/eliminar hábitos.
- `app/routes/checks.py`: marcar/desmarcar checks (HTMX).
- `app/templates/`: templates Jinja2.
- `app/static/styles.css`: estilo visual minimalista oscuro.
- `fly.toml`: configuración de deploy en Fly.
- `DEPLOY.md`: pasos de despliegue y verificación.

---

## Modelo de datos actual

### `Habit`

- `id` (PK)
- `name`
- `goal` (texto opcional)
- `category` (ej: Dinero, Salud, Fitness, Desarrollo personal, Adicciones, Estudio)
- `cadence` (`daily`, `weekly`, `monthly`, `yearly`)
- `habit_kind` (`positive` o `avoid`)
- `active` (bool)

### `HabitCheck`

- `habit_id` (PK compuesta + FK)
- `check_date` (PK compuesta, tipo fecha)
- `completed` (bool)
- `check_at` (timestamp ISO string, usado para rachas con horas/minutos)
- `notes` (opcional)

---

## Lógica de negocio clave

### Hábitos `positive`

- Se marcan como logrados por fecha (`completed=true`).
- Progresos agregados:
  - Semana: conteo de días cumplidos en la semana (`X/7`).
  - Mes: conteo sobre días del mes (`X/total_days`).
  - Año: conteo sobre días del año (`X/days_in_year`).

### Hábitos `avoid`

- Se marca el día de fallo.
- La racha se calcula como tiempo transcurrido desde la última marca (`check_at`):
  - formato mostrado: `Xd Yh Zm`.
- Si no hay marca reciente, no hay racha mostrada todavía.

---

## Endpoints principales

### Vistas

- `GET /` -> redirige a `/day`
- `GET /day`
- `GET /week`
- `GET /month`
- `GET /year`
- `GET /healthz`

### Hábitos

- `POST /habits/create`
- `POST /habits/{habit_id}/update`
- `POST /habits/{habit_id}/delete`

Rutas de resguardo para evitar `405` por GET accidental:

- `GET /habits/create` -> redirige a `/day`
- `GET /habits/{habit_id}/update` -> redirige a `/day`

### Checks

- `POST /checks/set`

Recibe `habit_id`, `date`, `completed` y devuelve HTML parcial del botón para HTMX.

---

## UI y diseño

- Estilo minimalista oscuro (negro/azul oscuro).
- Vistas basadas en tarjetas (`cards`) para día/semana/mes/año.
- Botones de check:
  - `positive`: `✚`/`✔`
  - `avoid`: `◯`/`✖`

---

## Deploy en Fly.io

Configuración relevante en `fly.toml`:

- App: `topuria-habits`
- `SQLITE_PATH=/data/sqlite.db`
- `TZ=UTC`
- Volumen montado en `/data`

Flujo típico:

1. `fly deploy`
2. revisar logs (`fly logs --tail`)
3. validar health (`/healthz`)

El volumen mantiene los datos entre deploys/restarts.

---

## Comandos útiles (local)

- Crear venv:
  - `python3 -m venv .venv`
- Instalar deps:
  - `.venv/bin/pip install -r requirements.txt`
- Ejecutar app local:
  - `SQLITE_PATH=./sqlite.db .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Check sintaxis:
  - `.venv/bin/python3 -m py_compile app/**/*.py`

---

## Pendientes/ideas futuras

- Ajustar definición de “objetivo cumplido” por período con umbral configurable (no siempre 100% de días).
- Agregar autenticación ligera (token/password) para proteger URL pública.
- Export/import de datos para backups manuales.
- Filtros por categoría en vistas.
- Mejor visualización de rachas y estadísticas históricas.

