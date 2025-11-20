# FunctionLab API (split repo)

## Run (Docker)

```sh
docker compose up --build
```

API: <http://localhost:8000>  
Kafka broker (inside network): `kafka:9092`

## Env

See `.env` for API/Kafka variables. Engine calls are not implemented yet; routers still import engine code and are marked with `TODO(engine via Kafka)`.

Next step: implement Kafka producer/consumer in `api/kafka/*` and replace direct engine imports in route handlers with request/response over Kafka.

