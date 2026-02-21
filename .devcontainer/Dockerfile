FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace

RUN apt-get update && apt-get install -y \
  build-essential \
  libpq-dev \
  curl \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip