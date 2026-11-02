# Imagen oficial ligera: reduce tamaño y mantiene una base reproducible.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# Las dependencias cambian menos que el código; esta capa se reutiliza en rebuilds.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# El código se copia después para no invalidar la capa de dependencias en cada cambio.
COPY app.py .

# La aplicación no requiere privilegios de root.
RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "2", "app:app"]
