# Build Vue.js frontend
FROM node:20-alpine as build-stage

ARG VUE_APP_VERSION
ENV VUE_APP_VERSION=${VUE_APP_VERSION}

WORKDIR /app
COPY ./frontend/package*.json ./
RUN npm install --verbose
COPY ./frontend/ ./
RUN npm run build --verbose

# Setup Container and install Flask backend
FROM python:3.11-alpine as deploy-stage

# Set environment variables
ENV PYTHONIOENCODING=UTF-8
ENV THEME=Default

WORKDIR /api
COPY ./backend/requirements.txt ./

# Install build dependencies and system libraries
RUN apk add --no-cache \
    build-base \
    gcc \
    g++ \
    make \
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
    nginx \
    curl \
    libxml2-dev \      # Correct placement inside apk add
    libxslt-dev        # Correct placement inside apk add

# Install Docker Compose 2.x as a standalone binary
RUN curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose

# Upgrade pip, setuptools, and wheel
RUN​⬤