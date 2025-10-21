# Utiliser une image Python de base
FROM python:3.11-slim

# Mettre à jour apt et installer les dépendances nécessaires pour WeasyPrint
# Note: Ces sont les paquets standard pour Pango, Cairo, etc. sur Debian/Ubuntu.
RUN apt-get update \ 
    && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-xlib-2.0-0 \
    libxml2-dev \
    libxslt-dev \
    libopenjp2-7 \
    zlib1g \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configurer l'environnement
WORKDIR /app

# Copier les fichiers d'exigences et installer les paquets Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code
COPY . .

# Définir la commande de démarrage
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
