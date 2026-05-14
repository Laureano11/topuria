# Topuria — Habit Tracker

> Minimalista web para seguimiento de hábitos, rachas y objetivos anuales.

Descripción
- Topuria es una aplicación web ligera que permite registrar hábitos diarios, semanales, mensuales y anuales, visualizar progreso por categoría, gestionar rachas y gamificar el avance mediante un personaje con atributos.
- La UI está renderizada con plantillas Jinja2 y las rutas y lógica de backend están implementadas en FastAPI. La persistencia usa SQLite y se crean datos demo al iniciarse si la DB está vacía.

Estructura principal
- Código: `app/`
- Rutas principales: `app/routes/` (views, habits, checks)
- Modelos y DB: `app/models.py`, `app/db.py`
- Plantillas y estáticos: `app/templates/`, `app/static/`

Requisitos
- Python 3.10+ (recomendado)
- Git
- (Opcional) Docker

Instalación y ejecución local (paso a paso)

1. Clonar el repositorio

```bash
git clone <REPO_URL> topuria
cd topuria
```

2. Crear y activar un entorno virtual

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Instalar dependencias

```bash
pip install -r requirements.txt
```

4. (Opcional) Definir ubicación de la base de datos

Por defecto la app crea `sqlite.db` en la carpeta del proyecto. Para usar una ruta específica (o un volumen persistente), exporta `SQLITE_PATH` antes de arrancar:

```bash
export SQLITE_PATH=/ruta/absoluta/mi_topuria_sqlite.db
```

Nota: en entornos como Fly.io, si existe `/data` la app apuntará a `/data/sqlite.db` automáticamente.

5. Ejecutar la aplicación en modo desarrollo

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

6. Abrir en el navegador

Visita http://127.0.0.1:8000 . Punto de comprobación: http://127.0.0.1:8000/healthz devuelve `{"ok": true}`.

Datos de ejemplo
- Al iniciar la aplicación por primera vez el módulo `app/db.py` crea las tablas y si la DB está vacía siembra datos demo (hábitos y eventos). Esto facilita probar la UI sin acciones previas.

Persistencia y despliegue
- Para producción y persistencia de datos, monta o apunta `SQLITE_PATH` a un volumen persistente.
- Hay un `Dockerfile` y `fly.toml` en el proyecto para despliegues containerizados; un flujo simple con Docker:

```bash
docker build -t topuria .
docker run -p 8000:8000 --env SQLITE_PATH=/data/sqlite.db topuria
```

Consejos para desarrolladores
- Punto de entrada local: `app/main.py` crea la app FastAPI y monta las rutas y plantillas.
- Código de negocio: `app/dashboard.py` contiene la lógica para construir el contexto (estadísticas, rachas, character, etc.).
- Modelos: `app/models.py` (SQLModel) define `Habit`, `HabitCheck`, `HabitEvent`.
- DB y migraciones mínimas: `app/db.py` crea tablas, añade columnas faltantes y migra checks antiguos a eventos.

Resolución de problemas
- Si no aparecen plantillas o estáticos, verifica que `app/templates/` y `app/static/` existen y contienen archivos.
- Si la app no inicia por permisos en SQLite, prueba apuntar `SQLITE_PATH` a una ruta con permisos de escritura.



----

