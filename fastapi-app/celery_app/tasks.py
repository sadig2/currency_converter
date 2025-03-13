# from .worker import celery_app
import logging

# import httpx

logger = logging.getLogger(__name__)


# @celery_app.task
# def debug_task():
#     logger.info("DEBUG TASK EXECUTED - THIS SHOULD APPEAR IN DOCKER LOGS")
#     print("PRINT STATEMENT - THIS SHOULD ALSO APPEAR")
#     return "Success"


# @celery_app.task
# def update_exchange_rates():
#     try:
#         with httpx.Client() as client:
#             response = client.get(
#                 "https://api.nbp.pl/api/exchangerates/tables/A/",
#                 headers={"Accept": "application/json"},
#             )
#             response.raise_for_status()
#             data = response.json()[0]["rates"]
#             logger.info("data queals: ", data)
# db = SessionLocal()
# try:
#     for rate in data:
#         db.merge(
#             ExchangeRate(
#                 currency=rate["code"],
#                 rate=rate["ask"],
#                 last_updated=datetime.utcnow(),
#             )
#         )
#     db.commit()
#     logger.info(f"Updated {len(data)} exchange rates")
# finally:
#     db.close()

# except Exception as e:
#     logger.error(f"Failed to update exchange rates: {str(e)}")

import httpx

with httpx.Client() as client:
    response = client.get(
        "https://api.nbp.pl/api/exchangerates/tables/A/",
        headers={"Accept": "application/json"},
    )
    response.raise_for_status()
    data = response.json()[0]["rates"]
    logger.info("data queals: ", data)
    for cur in data:
        print(f'{cur["code"]} -- {cur["mid"]} ')
