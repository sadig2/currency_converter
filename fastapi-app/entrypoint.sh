#!/bin/sh

# Wait for database
# until PGPASSWORD=$POSTGRES_PASSWORD psql -h "db" -U "youruser" -d "yourdb" -c '\q'; do
#   >&2 echo "Postgres is unavailable - sleeping"
#   sleep 1
# done

# Run migrations
alembic upgrade head

# Load initial data
python3 fixture.py

# Start application
exec "$@"