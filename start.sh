#!/bin/sh
set -e

# Run migrations first
alembic upgrade head

# Start the worker in the background
python worker.py &

# Start the API in the foreground, replacing the shell process.
# 'exec' makes uvicorn PID 1 so Render sees the port bind directly.
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
