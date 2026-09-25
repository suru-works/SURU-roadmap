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

Supuestos de `traefik/traefik.yml` que este compose da por hechos (mismo patrón que el ingress real de `suru-infra`, privado): entrypoints `web` (:80, redirige a HTTPS) y `websecure` (:443), un certificate resolver ACME llamado `le` y `providers.docker.exposedByDefault=false`. Cada router declara `entrypoints=websecure` y `tls.certresolver=le`; con solo `tls=true` Traefik serviría su certificado autofirmado por defecto.

```yaml
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
      - "127.0.0.1:8080:8080"    # Dashboard: solo loopback (plano admin, vía VPN/SSH); nunca en el ingress
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik/traefik.yml:/etc/traefik/traefik.yml:ro
      - ./traefik/dynamic:/etc/traefik/dynamic:ro
      - traefik-certs:/certs
    networks: [suruworks-net]

  postgres:
    image: postgres:17-alpine
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
    # Sin ports: los clientes llegan por suruworks-net (nats://nats:4222); nada se publica en el host

  minio:
    # ⚠ Imagen sin artefacto: MinIO CE está archivado y Docker Hub ya no sirve minio/minio (ver nota abajo)
    image: minio/minio:latest
    restart: unless-stopped
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ACCESS_KEY}
      MINIO_ROOT_PASSWORD: ${MINIO_SECRET_KEY}
    volumes: [minio-data:/data]
    networks: [suruworks-net]
    # Sin labels Traefik: la consola (:9001) es plano admin, solo VPN/LAN, nunca en el ingress público

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
      SPRING_DATA_REDIS_URL: redis://redis:6379/0
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
      - "traefik.http.routers.auth.entrypoints=websecure"
      - "traefik.http.routers.auth.tls.certresolver=le"
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
      - "traefik.http.routers.content.entrypoints=websecure"
      - "traefik.http.routers.content.tls.certresolver=le"
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
      - "traefik.http.routers.image3d.entrypoints=websecure"
      - "traefik.http.routers.image3d.tls.certresolver=le"
      - "traefik.http.services.image3d.loadbalancer.server.port=8000"
    # Sin reserva de GPU: la regla de colocación (homelab-topology.md §2) manda la GPU al rig,
    # con servicios nativos Windows fuera de Docker y proxiados por Traefik vía LAN

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
      AUTH_JWKS_URL: http://auth-service:8080/auth/.well-known/jwks.json
    networks: [suruworks-net]
    depends_on:
      postgres: {condition: service_healthy}
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.analytics.rule=Host(`${DOMAIN}`) && PathPrefix(`/analytics`)"
      - "traefik.http.routers.analytics.entrypoints=websecure"
      - "traefik.http.routers.analytics.tls.certresolver=le"
      - "traefik.http.services.analytics.loadbalancer.server.port=8080"
    # El JWT se valida en el servicio (JWKS local, como el resto); Traefik no trae middleware JWT nativo.
    # Si algún día se quiere el gate en el edge, es un middleware forwardAuth declarado en traefik/dynamic
```

> ⚠ **MinIO: la imagen de referencia ya no existe.** MinIO CE entró en modo mantenimiento (dic-2025), su repositorio fue archivado (abr-2026) y Docker Hub eliminó el namespace `minio` (sep-2026), así que `minio/minio:latest` ya no se puede descargar (el 2026-09-25 `docker manifest inspect minio/minio:latest` respondió `denied: requested access to the resource is denied`, mientras `nats:2.10-alpine` resolvía normal). Evidencia: [lobehub#9845](https://github.com/lobehub/lobehub/issues/9845), [VONNG — MinIO is Dead](https://blog.vonng.com/en/db/minio-is-dead/), [StableBuild](https://www.stablebuild.com/blog/minio-images-disappeared-from-docker-hub). El bloque se deja tal cual como marcador del almacenamiento S3-compatible: el reemplazo (otra implementación S3 o S3 administrado) es una decisión pendiente del dueño y no se elige aquí.

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

Publicado solo en el loopback del nodo (`127.0.0.1:8080`): se consulta desde el plano de administración (VPN + túnel SSH), nunca por el ingress público ([homelab-topology.md](homelab-topology.md) §1). Muestra todos los routers, servicios y middlewares activos en tiempo real. Desactivar en producción vía `traefik.yml`.

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
