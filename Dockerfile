FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (LibreOffice FIX)
RUN apt-get update && apt-get install -y \
    libreoffice \
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-common \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run server
CMD ["gunicorn", "cd_parser.wsgi:application", "--bind", "0.0.0.0:10000"]