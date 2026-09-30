FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc pkg-config default-libmysqlclient-dev && rm -rf /var/lib/apt/lists/*
COPY backend/requirements /app/requirements
RUN pip install --no-cache-dir -r requirements/production.txt
COPY backend /app/backend
COPY config /app/config
WORKDIR /app/backend
ENV DJANGO_SETTINGS_MODULE=config.settings.production
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
