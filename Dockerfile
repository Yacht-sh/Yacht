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
    libxml2-dev \      # Additional dependencies
    libxslt-dev        # Additional dependencies

# Install Docker Compose 2.x as a standalone binary
RUN curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose

# Upgrade pip, setuptools, and wheel
RUN pip3 install --upgrade pip setuptools wheel

# Install Python packages from requirements.txt
RUN pip3 install -r requirements.txt --no-cache-dir --verbose

# Install SASS via gem
RUN gem install sass --verbose

# Clean up build dependencies
RUN apk del --purge build-base && \
    rm -rf /root/.cache /tmp/*

# Copy the backend code
COPY ./backend/ ./

# Expose ports and define the command to run the application
EXPOSE 5000
CMD ["python3", "app.py"]