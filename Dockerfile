# Build Vue.js frontend
FROM node:14.5.0-alpine as build-stage

ARG VUE_APP_VERSION
ENV VUE_APP_VERSION=${VUE_APP_VERSION}

WORKDIR /app
COPY ./frontend/package*.json ./
RUN npm install --verbose
COPY ./frontend/ ./
RUN npm run build --verbose

# Setup Container and install Flask
FROM lsiobase/alpine:3.15 as deploy-stage
# MAINTANER Your Name "info@selfhosted.pro"

# Set environment variables
ENV PYTHONIOENCODING=UTF-8
ENV THEME=Default

WORKDIR /api
COPY ./backend/requirements.txt ./

# Install Dependancies
RUN \
	echo "**** install build packages ****" && \
	apk add --no-cache --virtual=build-dependencies \
	g++ \
	make \
	python3-dev \
	libffi-dev \
	mysql-dev \
	postgresql-dev \
	ruby-dev &&\
	echo "**** install packages ****" && \
	apk add --no-cache \
	python3 \
	py3-pip \
	nginx &&\
	pip3 install --upgrade pip setuptools &&\
	gem install sass &&\
	echo "**** Installing Python Modules ****" && \
	pip3 install wheel &&\
	pip3 install -r requirements.txt
RUN apk del --purge build-dependencies && \
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
