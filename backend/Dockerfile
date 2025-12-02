# 1. BAZNA SLIKA
FROM python:3.11-slim

# 2. POSTAVKA RADNOG DIREKTORIJA
WORKDIR /app

# 3. INSTALACIJA PYTHON PAKETA
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. KOPIRANJE APLIKACIJSKOG KODA
COPY . .

# 5. EKSPOZIRANJE PORTA
EXPOSE 8000

# 6. DEFAULTNA KOMANDA ZA POKRETANJE (Čista, bez sleep-a, oslanjamo se na docker-compose healthcheck)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]