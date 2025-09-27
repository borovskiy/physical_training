FROM python:3.12-alpine

# системные зависимости (если собираете wheels)
RUN apk add --no-cache \
    build-base \
    libffi-dev \
    openssl-dev \
    curl-dev \
    git

COPY req.txt .
RUN pip install --no-cache-dir -r req.txt

COPY . .

ENV PYTHONPATH=/app
RUN cd app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]