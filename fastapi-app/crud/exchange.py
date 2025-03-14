import asyncio
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import List, Dict

from core.models import ExchangeRate, db_helper


async def fetch_exchange_rates() -> List[Dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.nbp.pl/api/exchangerates/tables/A/",
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        data = response.json()
        return data[0]["rates"]


async def save_rates(session: AsyncSession, rates: List[Dict]):
    rate_data = [
        {
            "code": rate["code"],
            "rate": rate["mid"],
        }
        for rate in rates
    ]

    # Bulk insert using SQLAlchemy Core for maximum efficiency
    # await session.execute(ExchangeRate.__table__.insert().values(rate_data))

    # Alternative ORM bulk insert method
    session.add_all([ExchangeRate(**d) for d in rate_data])

    await session.commit()


async def async_main():

    rates = await fetch_exchange_rates()

    async with db_helper.session_factory() as session:
        await session.execute(ExchangeRate.__table__.delete())
        await session.commit()

        await save_rates(session, rates)
        print(f"Inserted {len(rates)} exchange rates")

        result = await session.execute(
            select(ExchangeRate).where(ExchangeRate.code == "USD")
        )
        usd_rate = result.scalar_one()
        print(f"Current USD rate: {usd_rate.rate}")


if __name__ == "__main__":
    asyncio.run(async_main())
