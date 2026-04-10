# Build Vue.js frontend
FROM node:20-bookworm-slim AS build-stage

ARG VUE_APP_VERSION
ENV VUE_APP_VERSION=${VUE_APP_VERSION}

WORKDIR /app
COPY ./frontend/package*.json ./
RUN npm ci --legacy-peer-deps --no-audit --no-fund
COPY ./frontend/ ./
RUN npm run build

# Build Python wheels in an isolated stage so compiler toolchains do not land in runtime.
FROM python:3.11-slim AS python-wheel-builder

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
    ca-certificates \
    && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip setuptools wheel && \
    pip3 wheel --wheel-dir /wheels -r requirements.txt setuptools

# Runtime image
FROM python:3.11-slim AS deploy-stage

ENV PYTHONIOENCODING=UTF-8
ENV THEME=Default
ENV PYTHONPATH=/api

WORKDIR /api
COPY ./backend/requirements.txt ./

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    nginx \
    docker-compose \
    ca-certificates \
    bash \
    libpq5 \
    libmariadb3 \
    libjpeg62-turbo \
    && \
    rm -rf /var/lib/apt/lists/*

COPY --from=python-wheel-builder /wheels /wheels

RUN pip3 install --no-cache-dir --no-index --find-links=/wheels setuptools && \
    pip3 install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt && \
    rm -rf /wheels

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
