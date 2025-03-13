import httpx
from fastapi import HTTPException


async def fetch_exchange_rates():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.nbp.pl/api/exchangerates/tables/A/"
            )
            response.raise_for_status()
            data = response.json()[0]["rates"]
            return {rate["code"]: rate["ask"] for rate in data}
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=503, detail=f"Failed to fetch rates from NBP API: {str(e)}"
        )
