#!/bin/bash

# Script de démarrage pour Fact-Checker IA v3.2.1

echo "=========================================="
echo "   🔍 Fact-Checker IA v3.2.1"
echo "=========================================="
echo ""

# Chemin du projet = dossier du script
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# Vérification de l'environnement virtuel
if [ ! -d "venv" ]; then
    echo "⚠️  Environnement virtuel non trouvé"
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
    ./venv/bin/pip install --upgrade pip
fi

# Installation des dépendances
echo "📦 Installation des dépendances..."
./venv/bin/pip install -q -r requirements.txt

# Vérification du fichier .env
if [ ! -f ".env" ]; then
    echo "⚠️  Fichier .env non trouvé"
    echo "📝 Création depuis env.template..."
    cp env.template .env
    echo "❗ IMPORTANT: Éditez .env avec vos clés API avant de continuer"
    exit 1
fi

# Lancement de l'application
echo ""
echo "🚀 Lancement de l'application..."
echo "📍 URL: http://localhost:8501"
echo ""
echo "Pour arrêter: Ctrl+C"
echo ""

./venv/bin/streamlit run src/ui/app.py --server.port 8501