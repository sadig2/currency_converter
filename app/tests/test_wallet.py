from fastapi import status
from src.auth.utils import hash_password
import pytest


# @pytest.mark.asyncio
async def test_get_request(client, db_session):
    # Test a simple healthcheck endpoint
    response = client.get("/api/test")

    # # Verify response status code
    assert response.status_code == status.HTTP_200_OK

    # # Verify response content
    # assert response.json() == {"status": "ok"}

    # print(dir(db_session))

    result = client.post(
        "/api/authenticate/register",
        json={"username": "sadig", "password": "qwerty"},
    )
    print(result.content)
    assert result.status_code == status.HTTP_200_OK

    # Verify database connection by checking SQLAlchemy engine
    # assert db_session.bind.url == settings.database_url
