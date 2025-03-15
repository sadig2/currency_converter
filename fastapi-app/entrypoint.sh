#!/bin/bash
set -e

echo "meowka" > out.txt

# Run database migrations
alembic downgrade base
alembic revision --autogenerate -m "create user table"
alembic upgrade head

# Load initial data
python3 fixture.py

# Start the main application
exec "$@"