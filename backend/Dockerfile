# 1. BAZNA SLIKA
FROM python:3.11-slim

# 2. POSTAVKA RADNOG DIREKTORIJA
WORKDIR /app

# 3. INSTALACIJA SYSTEM DEPENDENCIES
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    gnupg \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 4. INSTALACIJA MONGOSH ZA HEALTHCHECK (Updated method)
RUN wget -qO - https://pgp.mongodb.com/server-6.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb.gpg \
    && echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb.gpg ] https://repo.mongodb.org/apt/debian bullseye/mongodb-org/6.0 main" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list \
    && apt-get update \
    && apt-get install -y mongodb-mongosh \
    && rm -rf /var/lib/apt/lists/*

# 5. KOPIRANJE I INSTALACIJA PYTHON PAKETA
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. KOPIRANJE APLIKACIJSKOG KODA
COPY . .

# 7. KREIRANJE LOG FOLDERA
RUN mkdir -p /app/logs

# 8. EKSPOZIRANJE PORTA
EXPOSE 8000

# 9. DEFAULTNA KOMANDA ZA POKRETANJE
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]