#!/bin/sh
set -e

# Run migrations first
alembic upgrade head

# Start the worker in the background
python worker.py &

# Start the API in the foreground (this keeps the container alive)
uvicorn app.main:app --host 0.0.0.0 --port $PORT
