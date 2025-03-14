import asyncpg
import asyncio
import os


async def test():
    print("Connection successful!", os.getenv("POSTGRES_SERVER"))
    conn = await asyncpg.connect(
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        database=os.getenv("POSTGRES_DB"),
        host=os.getenv("POSTGRES_SERVER"),
        port=os.getenv("POSTGRES_PORT"),
    )
    await conn.close()


asyncio.run(test())
