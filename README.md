# Fact-Checker IA v3.2.1

Agent de vérification de faits intelligent avec LangGraph + GPT-4o-mini + Tavily.

## 🚀 Démarrage Rapide

```bash
# Installation
pip install -r requirements.txt

# Configuration
cp env.template .env
# Ajouter OPENAI_API_KEY et TAVILY_API_KEY dans .env

# Lancement
streamlit run src/ui/app.py
```

### Activer le hook anti-secrets (recommandé)

Empêche d'accidentellement committer des clés API ou des fichiers `.env` :

```bash
git config core.hooksPath .githooks
```

## 📁 Structure

```
Cnews/
├── docs/               # Documentation complète
│   ├── README.md       # Guide utilisateur détaillé
│   └── FICHE_TECHNIQUE.md  # Architecture technique
├── src/                # Code source
│   ├── agents/         # Agents LangGraph
│   ├── ui/             # Interface Streamlit
│   ├── utils/          # Utilitaires (whitelist, persistence, etc.)
│   └── domain/         # Modèles de données
├── tests/              # Tests unitaires (58/61 passants)
├── *.db                # Bases de données SQLite
└── requirements.txt    # Dépendances Python
```

## 🔧 Commandes

```bash
# Tests
pytest tests/ -v

# Démarrer le serveur
./start.sh

# Interface web
http://localhost:8501
```

## 📚 Documentation

Voir `docs/` pour la documentation complète.

## 🎯 Fonctionnalités

- ✅ Vérification de faits avec whitelist 6 tiers (~200 domaines)
- ✅ Scoring de crédibilité pondéré
- ✅ Interface Streamlit transparente
- ✅ Feedback utilisateur persisté
- ✅ Tests unitaires (95% coverage)

**Version**: 3.2.1 | **Statut**: Production Ready
