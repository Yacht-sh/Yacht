# Build Vue.js frontend
FROM node:20-bookworm-slim AS build-stage

ARG VUE_APP_VERSION
ENV VUE_APP_VERSION=${VUE_APP_VERSION}

WORKDIR /app
COPY ./frontend/package*.json ./
RUN npm ci --legacy-peer-deps --no-audit --no-fund
COPY ./frontend/ ./
RUN npm run build

# Runtime image
FROM python:3.14-slim AS deploy-stage

ARG DOCKER_COMPOSE_VERSION=v2.40.3

ENV PYTHONIOENCODING=UTF-8
ENV THEME=Default
ENV PYTHONPATH=/api

WORKDIR /api
COPY ./backend/requirements.txt ./

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    default-libmysqlclient-dev \
    libjpeg-dev \
    zlib1g-dev \
    libyaml-dev \
    python3-dev \
    nginx \
    curl \
    ca-certificates \
    bash && \
    rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    arch="$(uname -m)"; \
    case "${arch}" in \
      x86_64) compose_arch="x86_64" ;; \
      aarch64) compose_arch="aarch64" ;; \
      armv7l) compose_arch="armv7" ;; \
      armv6l) compose_arch="armv6" ;; \
      ppc64le) compose_arch="ppc64le" ;; \
      s390x) compose_arch="s390x" ;; \
      riscv64) compose_arch="riscv64" ;; \
      *) echo "Unsupported architecture: ${arch}" && exit 1 ;; \
    esac; \
    curl -fL "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-linux-${compose_arch}" -o /usr/local/bin/docker-compose; \
    chmod +x /usr/local/bin/docker-compose

RUN pip3 install --upgrade pip setuptools wheel && \
    pip3 install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove \
      build-essential \
      pkg-config \
      libffi-dev \
      libssl-dev \
      libpq-dev \
      default-libmysqlclient-dev \
      libjpeg-dev \
      zlib1g-dev \
      libyaml-dev \
      python3-dev && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd -r abc && useradd -r -g abc abc

COPY ./backend/ /api/
COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./docker/start.sh /usr/local/bin/start.sh
COPY --from=build-stage /app/dist /app

RUN chmod +x /usr/local/bin/start.sh && \
    mkdir -p /config/compose /var/www/client_body_temp /var/www/proxy_temp && \
    chown -R abc:abc /app /config /var/www

VOLUME /config
EXPOSE 8000
CMD ["/usr/local/bin/start.sh"]
