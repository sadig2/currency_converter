#!/bin/bash
set -e

# Run database migrations
# alembic downgrade base
# alembic revision --autogenerate -m "create user table"

# cd src
alembic upgrade head

# Load initial data
python3 fixture.py

# Start the main application
exec "$@"