# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
# netcat is useful for waiting for other services
RUN apt-get update && apt-get install -y netcat-openbsd

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install channels_redis

# Copy project
COPY . /app/

# Expose port 8000
EXPOSE 8000

# Run Daphne
CMD ["sh", "-c", "daphne -b 0.0.0.0 -p ${PORT:-8000} chat.asgi:application"]
