FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app

WORKDIR $APP_HOME

RUN apk add --no-cache --virtual .build-deps \
    gcc musl-dev libffi-dev

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps

#COPY app/ .
COPY app/ ./app/

RUN adduser -D appuser
USER appuser

EXPOSE 80

CMD ["gunicorn", "-b", "0.0.0.0:80", "app.run:app"]
