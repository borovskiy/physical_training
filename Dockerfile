# --- base ---
FROM python:3.12-alpine AS base
RUN apk add --no-cache build-base libffi-dev openssl-dev curl-dev git
COPY req.txt .
RUN pip install --no-cache-dir -r req.txt
COPY . .
RUN cd app
ENV PYTHONPATH=/app
# --- api ---
FROM base AS api
EXPOSE 8000
CMD ["python", "-m", "main"]



# --- celery worker ---
FROM base AS celery
CMD ["celery", "-A", "celery_app:celery_app", "worker", "-l", "info", "-E"]

FROM base AS flower
EXPOSE 5555
CMD ["celery", "-A", "celery_app:celery_app", "flower", "--port=5555", "--broker=${AMQP_URL}", "--result-backend=${CELERY_RESULT_DB_URL}"]