#!/bin/bash
set -e

cd src
alembic upgrade head

# Load initial data
python3 fixture.py

# Start the main application
exec "$@"