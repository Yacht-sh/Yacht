FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /agent

COPY ./agent/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./agent/ /agent/

VOLUME /config

CMD ["python", "/agent/main.py"]
