FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /agent

COPY ./agent/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install Docker CLI + compose plugin so the agent can run `docker compose` commands
RUN set -eux; \
    apt-get update && \
    apt-get install -y --no-install-recommends \
      ca-certificates \
      curl \
      gnupg \
      iproute2 \
    && \
    install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg \
      -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc && \
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
      https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
      > /etc/apt/sources.list.d/docker.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends docker-ce-cli docker-compose-plugin && \
    rm -rf /var/lib/apt/lists/*

COPY ./agent/ /agent/

VOLUME /config

CMD ["python", "/agent/main.py"]
