FROM python:3.13 AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    gcc \
    vim \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*\
    cd


COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.13 as production

WORKDIR /app


COPY --from=builder /install /app/install


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV PATH="/app/install/bin:${PATH}"
ENV PYTHONPATH="/app/install/lib/python3.13/site-packages:${PYTHONPATH}"

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
COPY . .

ENTRYPOINT ["/entrypoint.sh"]