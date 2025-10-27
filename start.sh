#!/bin/bash

# Script de lancement du Fact-Checker Agent
# Corrigé et fonctionnel

echo "🔍 Fact-Checker Agent - Démarrage"
echo "=================================="

# Chemin du projet
PROJECT_DIR="/Users/rayanekryslak-medioub/Desktop/AlbertSchool1/Agentic/Cnews"
cd "$PROJECT_DIR"

# Vérifier l'environnement virtuel
if [ ! -d "venv" ]; then
    echo "❌ Environnement virtuel non trouvé. Création en cours..."
    python3 -m venv venv
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install streamlit plotly duckduckgo-search beautifulsoup4 \
        langchain langchain-openai langchain-community python-dotenv requests pydantic
fi

# Vérifier le fichier .env
if [ ! -f ".env" ]; then
    echo "⚠️  Fichier .env non trouvé. Création à partir du template..."
    if [ -f "env.template" ]; then
        cp env.template .env
        echo "✅ Fichier .env créé. Veuillez configurer votre OPENAI_API_KEY"
    fi
fi

# Lancement de Streamlit
echo ""
echo "🚀 Lancement de l'interface Streamlit..."
echo "📍 URL: http://localhost:8501"
echo ""
echo "Pour arrêter: Ctrl+C"
echo ""

./venv/bin/python -m streamlit run streamlit_fact_checker.py --server.port 8501