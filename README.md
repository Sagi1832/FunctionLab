## Kafka Infrastructure

- `docker compose -f docker-compose.kafka.yml up -d` — starts Kafka only.
- `docker compose -f docker-compose.kafka.yml up -d --build` — builds and starts Kafka plus the engine worker.
- Use `kafka:9092` inside the Docker network, or `localhost:9094` from the host.

