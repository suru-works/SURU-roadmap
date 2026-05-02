# SURUworks — Docker Compose Reference Architecture

> Configuración de referencia para el despliegue on-premise Day 1.
> Basado en la arquitectura de microservicios definida en `microservices-architecture.md`.

---

## Estructura de directorios

```
suruworks/
├── docker-compose.yml
├── docker-compose.override.yml    ← Dev: hot reload, debug ports
├── docker-compose.prod.yml        ← Prod: no dashboard, TLS
├── .env.example
├── traefik/
│   ├── traefik.yml
│   └── dynamic/
│       ├── tls.yml
│       └── middlewares.yml
├── infrastructure/
│   ├── postgres/
│   │   └── init-dbs.sql          ← CREATE DATABASE por servicio
│   ├── redis/
│   │   └── redis.conf
│   ├── nats/
│   │   └── nats.conf
│   └── minio/
└── services/
    ├── auth-service/
    ├── content-service/
    ├── image3d-service/
    └── ...
```

---

## docker-compose.yml (base)

```yaml
version: "3.9"

networks:
  suruworks-net:
    driver: bridge

volumes:
  postgres-data:
  redis-data:
  nats-data:
  minio-data:
  traefik-certs:

services:

  # ── INFRAESTRUCTURA ──────────────────────────────────────────────

  traefik:
    image: traefik:v3
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"    # Dashboard — desactivar en producción
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik/traefik.yml:/etc/traefik/traefik.yml:ro
      - ./traefik/dynamic:/etc/traefik/dynamic:ro
      - traefik-certs:/certs
    networks: [suruworks-net]

  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: suruworks
      POSTGRES_PASSWORD: ${POSTGRES_ROOT_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./infrastructure/postgres/init-dbs.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks: [suruworks-net]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U suruworks"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server /etc/redis/redis.conf
    volumes:
      - redis-data:/data
      - ./infrastructure/redis/redis.conf:/etc/redis/redis.conf:ro
    networks: [suruworks-net]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  nats:
    image: nats:2.10-alpine
    restart: unless-stopped
    command: ["-js", "-sd", "/data", "-c", "/etc/nats/nats.conf"]
    volumes:
      - nats-data:/data
      - ./infrastructure/nats/nats.conf:/etc/nats/nats.conf:ro
    networks: [suruworks-net]
    ports:
      - "4222:4222"   # Client connections (internal only in prod)

  minio:
    image: minio/minio:latest
    restart: unless-stopped
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ACCESS_KEY}
      MINIO_ROOT_PASSWORD: ${MINIO_SECRET_KEY}
    volumes: [minio-data:/data]
    networks: [suruworks-net]
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.minio-console.rule=Host(`storage.${DOMAIN}`)"
      - "traefik.http.routers.minio-console.service=minio-console"
      - "traefik.http.services.minio-console.loadbalancer.server.port=9001"
      - "traefik.http.routers.minio-console.tls=true"

  # ── SERVICIOS DE APLICACIÓN ─────────────────────────────────────

  auth-service:
    build:
      context: ./services/auth-service
      dockerfile: Dockerfile
    restart: unless-stopped
    environment:
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/auth_db
      SPRING_DATASOURCE_USERNAME: suruworks
      SPRING_DATASOURCE_PASSWORD: ${POSTGRES_ROOT_PASSWORD}
      SPRING_REDIS_URL: redis://redis:6379/0
      JWT_PRIVATE_KEY_PATH: /secrets/auth-private.pem
      JWT_PUBLIC_KEY_PATH: /secrets/auth-public.pem
      NATS_URL: nats://nats:4222
      APP_FRONTEND_URL: https://${DOMAIN}
    volumes:
      - ./secrets/auth:/secrets:ro
    networks: [suruworks-net]
    depends_on:
      postgres: {condition: service_healthy}
      redis: {condition: service_healthy}
      nats: {condition: service_started}
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.auth.rule=Host(`${DOMAIN}`) && PathPrefix(`/auth`)"
      - "traefik.http.routers.auth.tls=true"
      - "traefik.http.services.auth.loadbalancer.server.port=8080"

  content-service:
    build:
      context: ./services/content-service
      dockerfile: Dockerfile
    restart: unless-stopped
    environment:
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/content_db
      SPRING_DATASOURCE_USERNAME: suruworks
      SPRING_DATASOURCE_PASSWORD: ${POSTGRES_ROOT_PASSWORD}
      AUTH_JWKS_URL: http://auth-service:8080/auth/.well-known/jwks.json
    networks: [suruworks-net]
    depends_on:
      postgres: {condition: service_healthy}
      auth-service: {condition: service_started}
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.content.rule=Host(`${DOMAIN}`) && PathPrefix(`/content`)"
      - "traefik.http.routers.content.tls=true"
      - "traefik.http.services.content.loadbalancer.server.port=8080"

  image3d-service:
    build:
      context: ./services/image3d-service
      dockerfile: Dockerfile
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql://suruworks:${POSTGRES_ROOT_PASSWORD}@postgres:5432/image3d_db
      REDIS_URL: redis://redis:6379/1
      NATS_URL: nats://nats:4222
      MINIO_ENDPOINT: http://minio:9000
      MINIO_ACCESS_KEY: ${MINIO_ACCESS_KEY}
      MINIO_SECRET_KEY: ${MINIO_SECRET_KEY}
      AUTH_JWKS_URL: http://auth-service:8080/auth/.well-known/jwks.json
    networks: [suruworks-net]
    depends_on:
      postgres: {condition: service_healthy}
      redis: {condition: service_healthy}
      minio: {condition: service_started}
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.image3d.rule=Host(`${DOMAIN}`) && PathPrefix(`/tools/image-to-3d`)"
      - "traefik.http.routers.image3d.tls=true"
      - "traefik.http.services.image3d.loadbalancer.server.port=8000"
    # GPU support (descomentar si GPU disponible):
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: 1
    #           capabilities: [gpu]

  email-service:
    build:
      context: ./services/email-service
      dockerfile: Dockerfile
    restart: unless-stopped
    environment:
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/email_db
      SPRING_DATASOURCE_USERNAME: suruworks
      SPRING_DATASOURCE_PASSWORD: ${POSTGRES_ROOT_PASSWORD}
      NATS_URL: nats://nats:4222
      RESEND_API_KEY: ${RESEND_API_KEY}
      FROM_EMAIL: noreply@${DOMAIN}
    networks: [suruworks-net]
    depends_on:
      postgres: {condition: service_healthy}
      nats: {condition: service_started}
    # Sin label Traefik — solo consume eventos NATS, no expone HTTP público

  analytics-service:
    build:
      context: ./services/analytics-service
      dockerfile: Dockerfile
    restart: unless-stopped
    environment:
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/analytics_db
      SPRING_DATASOURCE_USERNAME: suruworks
      SPRING_DATASOURCE_PASSWORD: ${POSTGRES_ROOT_PASSWORD}
    networks: [suruworks-net]
    depends_on:
      postgres: {condition: service_healthy}
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.analytics.rule=Host(`${DOMAIN}`) && PathPrefix(`/analytics`)"
      - "traefik.http.routers.analytics.tls=true"
      - "traefik.http.middlewares.analytics-auth.plugin.jwt.required=true"
      - "traefik.http.routers.analytics.middlewares=analytics-auth"
      - "traefik.http.services.analytics.loadbalancer.server.port=8080"
```

---

## infrastructure/postgres/init-dbs.sql

```sql
-- Crear base de datos por servicio
CREATE DATABASE auth_db;
CREATE DATABASE content_db;
CREATE DATABASE profiles_db;
CREATE DATABASE registry_db;
CREATE DATABASE email_db;
CREATE DATABASE analytics_db;
CREATE DATABASE image3d_db;

-- Todos usando el usuario principal (simplificado para Day 1)
-- En producción: crear usuarios dedicados por DB con permisos mínimos
```

---

## .env.example

```bash
# Dominio
DOMAIN=suruworks.com

# PostgreSQL
POSTGRES_ROOT_PASSWORD=change-me-in-production

# MinIO (S3-compatible object storage)
MINIO_ACCESS_KEY=suruworks-admin
MINIO_SECRET_KEY=change-me-in-production

# Email
RESEND_API_KEY=re_xxxxxxxxxxxx

# JWT (generar con: openssl genrsa -out auth-private.pem 4096)
# Las claves van en ./secrets/auth/

# Monitoreo
GRAFANA_ADMIN_PASSWORD=change-me-in-production
```

---

## Comandos útiles

```bash
# Levantar toda la plataforma
docker compose up -d

# Ver logs de un servicio
docker compose logs -f auth-service

# Reiniciar un servicio específico
docker compose restart image3d-service

# Rebuild y restart después de cambios
docker compose up -d --build auth-service

# Ver estado de todos los servicios
docker compose ps

# Escalar un servicio (para load testing)
docker compose up -d --scale image3d-service=3

# Entrar al shell de PostgreSQL
docker compose exec postgres psql -U suruworks auth_db

# Entrar al shell de Redis
docker compose exec redis redis-cli
```

---

## Traefik Dashboard

Disponible en `http://localhost:8080` en desarrollo. Muestra todos los routers, servicios y middlewares activos en tiempo real. Desactivar en producción vía `traefik.yml`.

---

## Orden de inicio recomendado (troubleshooting)

```bash
# 1. Infraestructura base
docker compose up -d postgres redis nats minio traefik

# 2. Auth (todos dependen de él)
docker compose up -d auth-service

# 3. Resto de servicios
docker compose up -d content-service email-service analytics-service

# 4. Servicio pesado de AI
docker compose up -d image3d-service
```
