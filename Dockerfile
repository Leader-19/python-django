FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# =========================
# SYSTEM DEPENDENCIES
# =========================
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# =========================
# PYTHON DEPENDENCIES
# =========================
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# =========================
# PROJECT FILES
# =========================
COPY . .

# =========================
# STATIC FILES
# =========================
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "cd_parser.wsgi:application", "--bind", "0.0.0.0:8000"]