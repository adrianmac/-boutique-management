FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port (Railway sets PORT dynamically)
EXPOSE ${PORT:-8000}

# Run gunicorn bound to dynamic PORT (defaults to 8000 for local Docker)
CMD gunicorn boutique_management.wsgi:application --bind 0.0.0.0:${PORT:-8000}
