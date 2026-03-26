# Deploy en Fly.io (FastAPI + SQLite en volumen)

## 1. Requisitos

- Tener `flyctl` instalado: [https://fly.io/docs/flyctl/install/](https://fly.io/docs/flyctl/install/)
- Login: `fly auth login`

## 2. Crear app y volumen

1. En la carpeta del proyecto:
  - `fly launch --no-deploy --name topuria-habits`
2. Crear el volumen persistente (para `sqlite.db`):
  - `fly volumes create topuria_sqlite --region iad --size 1 --yes`

El `fly.toml` ya referencia este volumen en:

- `source = "topuria_sqlite"`
- `destination = "/data"`

## 3. Deploy

- `fly deploy`

El `fly.toml` configura:

- `SQLITE_PATH = "/data/sqlite.db"`
- `TZ = "UTC"`

## 4. Verificación de persistencia

1. Abrí la app en el navegador y marcá un check en `Día` o `Semana`.
2. Reiniciá la machine (sin redeploy) y verificá que el check siga:
  - `fly machines restart <machine-id>`
  - (podés obtener el `machine-id` con `fly machines list`)
3. Si preferís, también podés hacer un redeploy normal `fly deploy` y confirmar que no se pierden datos.

## 5. Check rápido de salud y logs

- Ver logs: `fly logs`
- Check de salud (en tu URL de la app): `/healthz`

