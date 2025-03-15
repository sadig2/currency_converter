import asyncio
from redis.asyncio import Redis
import httpx
from celery import Celery
from .worker import celery_app
import json


@celery_app.task
def sync():
    asyncio.run(update_exchange_rates())


async def fetch_rate(operation_type: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.nbp.pl/api/exchangerates/tables/{operation_type}/",
            headers={"Accept": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
        rates_data = response.json()[0]
        effective_date = rates_data["effectiveDate"]
        rates = rates_data["rates"]
        return rates


async def update_exchange_rates():
    """Async Celery task to update exchange rates in Redis"""
    try:

        mid1, mid2, trade = await asyncio.gather(
            fetch_rate("A"),
            fetch_rate("B"),
            fetch_rate("C"),
        )

        rate_mapping = {rate["code"]: str(rate["mid"]) for rate in mid1}
        rate_mapping2 = {rate["code"]: str(rate["mid"]) for rate in mid2}
        rate_mapping3 = {
            rate["code"]: json.dumps({"bid": rate["bid"], "ask": rate["ask"]})
            for rate in trade
        }

        redis = Redis.from_url("redis://redis:6379/0", socket_timeout=5)

        if not await redis.ping():
            return

        await redis.hset("mids", mapping=rate_mapping)
        await redis.hset("mids", mapping=rate_mapping2)
        await redis.hset("trade", mapping=rate_mapping3)
        await redis.expire("mids", 360)

        await redis.close()

    except Exception as e:
        raise
