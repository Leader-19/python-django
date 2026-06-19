# Use official Python image
FROM python:3.11-slim

# Prevent Python from writing pyc files + force logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Work directory
WORKDIR /app

# =========================
# SYSTEM DEPENDENCIES
# =========================
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    wget \
    libreoffice \
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-common \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

# =========================
# INSTALL PYTHON DEPENDENCIES
# =========================
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# =========================
# COPY PROJECT
# =========================
COPY . .

# =========================
# STATIC FILES
# =========================
RUN python manage.py collectstatic --noinput || true

# =========================
# OPEN PORT
# =========================
EXPOSE 8000

# =========================
# START SERVER
# =========================
CMD ["gunicorn", "cd_parser.wsgi:application", "--bind", "0.0.0.0:8000"]