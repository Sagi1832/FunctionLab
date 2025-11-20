## Database Diagnostics

Run the lightweight connectivity check script before starting the backend:

```
venv\Scripts\python scripts\db_check.py
```

The script loads `.env`, prints the parsed host/port/database, and verifies the connection with `SELECT 1`.

To seed a local test user (default `sagi1234` / `FunctionLab123!`), run:

```
venv\Scripts\python scripts\seed_user.py
```

Override with `SEED_USER_USERNAME` / `SEED_USER_PASSWORD` if needed.

## Kafka Infrastructure

- `docker compose -f docker-compose.kafka.yml up -d` — starts Kafka only.
- `docker compose -f docker-compose.kafka.yml up -d --build` — builds and starts Kafka plus the engine worker.
- Use `kafka:9092` inside the Docker network, or `localhost:9094` from the host.

