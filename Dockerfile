FROM python:3.12-slim

# Don't buffer Python output — logs appear immediately (important for a worker)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first, separately from code.
# Docker caches this layer, so changing your code doesn't reinstall everything.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the application code
COPY . .

# Default command runs the API. The worker overrides this in compose.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
