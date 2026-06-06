FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

COPY app/ ./app/
COPY tests/ ./tests/

ENV PATH="/install/bin:${PATH}" \
    PYTHONPATH="/build:/install/lib/python3.11/site-packages"

RUN pytest


FROM python:3.11-slim AS runtime

RUN groupadd --system app \
    && useradd --system --gid app --create-home app

WORKDIR /app

COPY --from=builder /install /usr/local
COPY app/ ./app/

USER app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 5000

CMD ["python", "-m", "app"]
