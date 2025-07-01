# Build Vue.js frontend
FROM node:20-alpine as build-stage

ARG VUE_APP_VERSION
ENV VUE_APP_VERSION=${VUE_APP_VERSION}

WORKDIR /app
COPY ./frontend/package*.json ./
RUN npm install --verbose
COPY ./frontend/ ./
RUN npm run build --verbose

# Setup Container and install Flask
FROM python:3.11-alpine as deploy-stage

# Set environment variables
ENV PYTHONIOENCODING=UTF-8
ENV THEME=Default

WORKDIR /api
COPY ./backend/requirements.txt ./

RUN apk add --no-cache \
    build-base \
    curl \
    libffi-dev \
    openssl-dev \
    musl-dev \
    postgresql-dev \
    mysql-dev \
    jpeg-dev \
    zlib-dev \
    yaml-dev \
    python3-dev \
    ruby-dev \
    nginx && \
    pip3 install --upgrade pip setuptools wheel && \
    pip3 install Cython && \
    pip3 install --no-cache-dir --force-reinstall PyYAML==5.4.1 && \
    pip3 install --use-pep517 aiostream==0.4.3 --no-cache-dir && \
    pip3 install --use-pep517 --use-deprecated=legacy-resolver -r requirements.txt --no-cache-dir

RUN curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose

RUN gem install sass --verbose

RUN apk del --purge build-base && \
    rm -rf /root/.cache /tmp/*

COPY ./backend/api ./
COPY ./backend/alembic /alembic
COPY root ./backend/alembic.ini /

# Vue
COPY --from=build-stage /app/dist /app
COPY nginx.conf /etc/nginx/

# Expose
VOLUME /config
EXPOSE 8000
