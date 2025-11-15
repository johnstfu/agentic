# 🔍 Vérificateur de Faits IA - Tavily + OpenAI

**Système intelligent de vérification automatique des faits basé sur l'IA**

> 📖 **Nouveau !** Consultez le [**GUIDE UTILISATEUR**](GUIDE_UTILISATEUR.md) pour un **guide complet en langage simple**, accessible à tous, même les non-informaticiens.

## 🎯 Vue d'ensemble

Ce projet est un **fact-checker intelligent** qui combine :
- **Tavily** : Recherche web avancée optimisée pour le fact-checking
- **OpenAI GPT-4** : Analyse intelligente des sources et génération de verdicts
- **LangGraph** : Workflow adaptatif avec Human-in-the-Loop (v3.0)
- **Streamlit** : Interface web intuitive et professionnelle

## 📦 Versions Disponibles

### v2.0 (Stable)
Architecture procédurale classique avec cache et rate limiting.

### v3.0 (LangGraph Edition) - NOUVEAU ✨
- **Human-in-the-Loop** : Validation humaine des sources et verdicts
- **Persistence Multi-Session** : Historique utilisateur avec SqliteSaver
- **Multi-Step Reasoning** : Workflow adaptatif selon contexte
- **Feedback Loop** : Collecte ratings et amélioration continue
- **Batch Processing** : Vérification parallèle de 10 claims
- **Explainability** : Trace complète du raisonnement

### Architecture v3.0
```
Utilisateur → Affirmation
    ↓
Tavily → Recherche sources
    ↓ [HITL]
Humain → Valide sources
    ↓
OpenAI → Analyse crédibilité (adaptatif)
    ↓
OpenAI → Génère verdict
    ↓ [HITL]
Humain → Révise verdict
    ↓
Publication + Feedback
```

---

## 🚀 Installation et Lancement

### Prérequis
- Python 3.9+
- Clés API OpenAI et Tavily

### Installation rapide
```bash
# 1. Cloner ou naviguer vers le projet
cd /path/to/Cnews

# 2. Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les clés API
cp env.template .env
# Éditer .env avec vos clés API
```

### Configuration des clés API

Créez un fichier `.env` avec :
```env
# OpenAI (pour l'analyse IA)
OPENAI_API_KEY=your-openai-api-key-here

# Tavily (pour la recherche web)
TAVILY_API_KEY=your-tavily-api-key-here
```

#### Obtenir les clés API

**OpenAI API Key:**
1. Créer un compte sur https://platform.openai.com
2. Aller dans API Keys
3. Créer une nouvelle clé
4. Ajouter des crédits ($5 minimum recommandé)

**Tavily API Key:**
1. Créer un compte sur https://tavily.com
2. Plan gratuit : 1000 requêtes/mois
3. Copier la clé API depuis le dashboard

### Lancement
```bash
# Avec le script de démarrage
./start.sh

# Ou directement
streamlit run app.py
```

**Interface accessible sur** : http://localhost:8501

### Sélection de Version

Dans l'interface, utiliser le sidebar pour choisir :
- **v2.0 (Stable)** : Système classique
- **v3.0 (LangGraph + HITL)** : Nouveau système avec interruptions

Pour v3.0, options disponibles :
- Activer/désactiver Human-in-the-Loop
- Définir un User ID pour l'historique
- Mode Simple ou Batch

---

## 📊 Fonctionnalités

### Interface utilisateur v2.0
- ✅ Saisie d'affirmation à vérifier
- ✅ Verdict clair (VÉRIFIÉ / NON VÉRIFIÉ / INCERTAIN)
- ✅ Score de véracité (0-100%)
- ✅ Affichage transparent des sources
- ✅ Filtrage des sources par crédibilité
- ✅ Métriques techniques (temps, nombre de sources)
- ✅ Export des résultats en JSON

### Nouvelles fonctionnalités v3.0
- ✨ **Human-in-the-Loop** : Validation manuelle des sources et verdicts
- ✨ **Historique utilisateur** : Voir les 10 dernières vérifications
- ✨ **Mode Batch** : Vérifier jusqu'à 10 claims en parallèle
- ✨ **Trace complète** : Timeline des décisions avec raisonnement
- ✨ **Feedback système** : Noter la qualité et signaler erreurs
- ✨ **Multi-step reasoning** : Recherche approfondie automatique si nécessaire
- ✨ **Export trace** : JSON complet pour audit

### Système de scoring

#### Crédibilité des sources (0.0 à 1.0)
- **0.95-1.0** : Institutions officielles (.gov, OMS, ONU)
- **0.85-0.95** : Sources scientifiques (universités, Nature, Science)
- **0.70-0.85** : Médias établis (Reuters, BBC, AFP, Le Monde)
- **0.50-0.70** : Médias généralistes reconnus
- **< 0.50** : Sources à vérifier

#### Score de véracité (0-100%)
- **81-100%** : VÉRIFIÉ - Confirmé par sources haute crédibilité
- **61-80%** : PROBABLEMENT VRAI - Majorité confirme
- **41-60%** : INCERTAIN - Sources contradictoires
- **21-40%** : PROBABLEMENT FAUX - Majorité conteste
- **0-20%** : CONTESTÉ - Confirmé faux par sources fiables

---

## 🧪 Exemples de Test

### Affirmations vraies
```
✅ "La Tour Eiffel mesure 330 mètres de hauteur"
✅ "L'eau bout à 100°C au niveau de la mer"
✅ "Emmanuel Macron est président de la France"
```

### Affirmations fausses
```
❌ "Le vaccin COVID-19 contient des puces 5G"
❌ "La Terre est plate"
❌ "Paris est la capitale de l'Espagne"
```

### Test rapide du backend
```bash
# Test de l'agent de fact-checking
python3 smart_fact_checker.py

# Résultat attendu :
# ✅ Tavily: 8 sources trouvées
# ✅ OpenAI: Verdict = ✅ VÉRIFIÉ, Score = 95%
```

---

## 🏗️ Structure du Projet

```
Cnews/
├── streamlit_fact_checker.py   # Interface Streamlit
├── smart_fact_checker.py       # Agent de fact-checking
├── start.sh                    # Script de démarrage
├── requirements.txt            # Dépendances Python
├── .env                        # Clés API (non versionné)
├── env.template                # Template pour .env
├── .gitignore                  # Fichiers à ignorer
└── README.md                   # Documentation
```

---

## 🔧 Architecture Technique

### smart_fact_checker.py
**Agent intelligent de vérification**
- Classe `SmartFactChecker`
- Recherche web via Tavily API
- Analyse de crédibilité dynamique avec OpenAI
- Génération de verdict avec justifications

**Méthode principale** : `verify_claim(claim: str) -> Dict`

### streamlit_fact_checker.py
**Interface utilisateur Streamlit**
- Design MIT Media Lab (minimaliste et professionnel)
- Affichage des sources avec badges de crédibilité
- Filtres de sources (crédibilité minimale, types)
- Export JSON des résultats
- Métriques techniques transparentes

---

## 🔒 Sécurité et Confidentialité

- ✅ Aucune donnée personnelle collectée
- ✅ Requêtes analysées en temps réel (pas de stockage)
- ✅ Communication chiffrée HTTPS
- ✅ Conforme RGPD
- ✅ Clés API stockées localement dans .env

---

## 🐛 Troubleshooting

### Erreur : "OPENAI_API_KEY manquante"
```bash
# Vérifier le fichier .env
cat .env

# Doit contenir :
OPENAI_API_KEY=your-openai-api-key-here
```

### Erreur : "TAVILY_API_KEY manquante"
```bash
# Ajouter dans .env
echo "TAVILY_API_KEY=your-tavily-api-key-here" >> .env
```

### Erreur : Module non trouvé
```bash
# Réinstaller les dépendances
pip install -r requirements.txt
```

### L'interface ne se lance pas
```bash
# Vérifier que Streamlit est installé
streamlit --version

# Vérifier le port 8501
lsof -i :8501

# Utiliser un autre port si nécessaire
streamlit run streamlit_fact_checker.py --server.port 8502
```

---

## 📈 Dépendances

```txt
streamlit>=1.28.0
plotly>=5.17.0
python-dotenv>=1.0.0
langchain>=0.1.0
langchain-openai>=0.0.2
tavily-python>=0.3.0
openai>=1.0.0
```

---

## 🚦 Méthodologie de Fact-Checking

### 1. Recherche (Tavily)
- Recherche multi-stratégies sur le web
- Priorisation des sources officielles
- Extraction du contenu pertinent

### 2. Analyse de crédibilité (OpenAI)
- Évaluation du type de source
- Attribution d'un score de confiance
- Analyse de la réputation et expertise

### 3. Analyse du claim (OpenAI)
- Comparaison avec les sources
- Identification des contradictions
- Position de chaque source (CONFIRME/INFIRME/NEUTRE)

### 4. Verdict final (OpenAI)
- Pondération selon la crédibilité
- Score de véracité global
- Recommandations pour l'utilisateur

---

## 🎨 Personnalisation

### Modifier le design Streamlit
Éditer le CSS dans `streamlit_fact_checker.py` (lignes 32-227)

### Ajouter des sources de confiance
Modifier le prompt système dans `smart_fact_checker.py` (lignes 146-183)

### Changer le modèle OpenAI
```python
# Dans smart_fact_checker.py, ligne 52
self.llm = ChatOpenAI(
    model="gpt-4o-mini",  # Changer ici
    temperature=0.1
)
```

---

## 📝 Licence

Projet éducatif - Libre d'utilisation pour la lutte contre la désinformation

---

## 🤝 Contribution

Pour contribuer :
1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit les changements (`git commit -m 'Ajout fonctionnalité'`)
4. Push vers la branche (`git push origin feature/amelioration`)
5. Ouvrir une Pull Request

---

## 🔗 Ressources

- [Documentation Tavily](https://tavily.com/docs)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [Streamlit Documentation](https://docs.streamlit.io)
- [LangChain Guide](https://python.langchain.com/docs/get_started/introduction)

---

## 🚀 Déploiement Production

### Prérequis Serveur
- **OS :** Linux (Ubuntu 20.04+ recommandé)
- **Python :** 3.9+
- **RAM :** 2GB minimum
- **Stockage :** 5GB minimum
- **Réseau :** Accès HTTPS à OpenAI + Tavily

### Configuration Production

1. **Variables d'environnement** :
```bash
# Créer .env depuis template
cp env.template .env

# Éditer avec vraies credentials
nano .env

# Sécuriser permissions
chmod 600 .env
```

2. **Installation dépendances** :
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

3. **Configuration Streamlit** :
```bash
# Créer .streamlit/config.toml
mkdir -p .streamlit
cat > .streamlit/config.toml <<EOF
[server]
port = 8501
address = "0.0.0.0"
headless = true
enableCORS = false

[browser]
gatherUsageStats = false

[theme]
base = "light"
EOF
```

4. **Lancement avec Systemd** :
```bash
# Créer /etc/systemd/system/verificateur-ia.service
[Unit]
Description=VérificateurIA Streamlit App
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/Cnews
Environment="PATH=/path/to/Cnews/venv/bin"
ExecStart=/path/to/Cnews/venv/bin/streamlit run app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Activer et démarrer
sudo systemctl enable verificateur-ia
sudo systemctl start verificateur-ia
```

### Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### HTTPS avec Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d votre-domaine.com
```

---

## 📊 Monitoring & Observabilité

### Métriques Clés

**Performance** :
- Latence moyenne vérification : < 20s
- Cache hit rate : > 40%
- Taux erreurs API : < 5%

**Usage** :
- Claims vérifiées / jour
- Utilisateurs uniques / semaine
- Verdicts "VÉRIFIÉ" vs "NON VÉRIFIÉ" (ratio)

### Logs

**Localisation** :
```bash
# Logs Streamlit
/var/log/streamlit/verificateur-ia.log

# Logs applicatifs
tail -f fact_checks.db  # SQLite persistence
```

**Monitoring en temps réel** :
```bash
# Surveiller logs
journalctl -u verificateur-ia -f

# Surveiller ressources
htop

# Surveiller base données
sqlite3 fact_checks.db "SELECT COUNT(*) FROM checkpoints;"
```

### Alertes

**Setup avec cron** :
```bash
# Script d'alerte (alert.sh)
#!/bin/bash
ERROR_COUNT=$(journalctl -u verificateur-ia --since "1 hour ago" | grep ERROR | wc -l)
if [ $ERROR_COUNT -gt 10 ]; then
    echo "⚠️ Plus de 10 erreurs dans la dernière heure" | mail -s "Alert VérificateurIA" admin@example.com
fi

# Ajouter au crontab
*/15 * * * * /path/to/alert.sh
```

### Dashboard Grafana (Optionnel)

1. Installer Prometheus + Grafana
2. Exporter métriques Streamlit
3. Créer dashboard avec :
   - Temps réponse moyen
   - Requêtes/minute
   - Erreurs API
   - Utilisation mémoire/CPU

---

## 🔧 Troubleshooting

### Problèmes Fréquents

#### 1. "Cannot operate on a closed database"

**Cause :** Connexion SQLite fermée prématurément  
**Solution :**
```python
# Vérifier que FactCheckerGraph.close() n'est pas appelé trop tôt
# Ou relancer l'app : Ctrl+C puis streamlit run app.py
```

#### 2. "Rate limit exceeded" (Tavily/OpenAI)

**Cause :** Trop de requêtes API  
**Solution :**
```python
# Augmenter délai dans src/agents/fact_checker.py
self.min_request_interval = 2.0  # Au lieu de 1.0
```

#### 3. "API key not found"

**Cause :** `.env` mal configuré  
**Solution :**
```bash
# Vérifier que .env existe
ls -la .env

# Vérifier contenu
cat .env | grep API_KEY

# Recharger environnement
source venv/bin/activate
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OPENAI_API_KEY'))"
```

#### 4. Interface Streamlit ne charge pas

**Cause :** Port occupé ou firewall  
**Solution :**
```bash
# Vérifier port disponible
lsof -i :8501

# Changer port
streamlit run app.py --server.port 8502

# Vérifier firewall
sudo ufw allow 8501/tcp
```

#### 5. Résultats non affichés

**Cause :** Bug UI ou cache Streamlit  
**Solution :**
```bash
# Vider cache Streamlit
rm -rf ~/.streamlit/cache

# Forcer rechargement : R dans le navigateur
```

#### 6. Performances lentes

**Cause :** Cache désactivé ou trop de requêtes  
**Solution :**
```python
# Activer cache dans Config
ENABLE_CACHE = True
CACHE_TTL = 3600  # 1h

# Vérifier hit rate
python -c "from src.utils.cache import SimpleCache; c = SimpleCache(); print(f'Hit rate: {c.hits / (c.hits + c.misses):.2%}')"
```

### Debug Mode

**Activer logs détaillés** :
```python
# Dans src/utils/logger.py
class FactCheckerLogger:
    def __init__(self):
        self.level = logging.DEBUG  # Au lieu de INFO
```

**Exécuter tests** :
```bash
# Tous les tests
pytest tests/ -v

# Tests spécifiques
pytest tests/test_shared_modules.py -v

# Avec coverage
pytest --cov=src tests/
```

### Support

**Documentation** :
- [GUIDE_UTILISATEUR.md](GUIDE_UTILISATEUR.md) - Guide simple
- [HYBRID_SEARCH_ARCHITECTURE.md](HYBRID_SEARCH_ARCHITECTURE.md) - Architecture technique
- [SECURITY_AUDIT.md](SECURITY_AUDIT.md) - Sécurité

**Logs & Issues** :
```bash
# Collecter logs pour debug
tar -czf logs_$(date +%Y%m%d).tar.gz \
    fact_checks.db \
    ~/.streamlit/ \
    /var/log/streamlit/

# Ouvrir issue GitHub avec logs
```

---

## 📈 Statistiques & Analytics

### Métriques Intégrées

**Consulter stats** :
```python
from src.utils.feedback import FeedbackManager

fm = FeedbackManager()
stats = fm.get_stats()
print(f"Total vérifications : {stats['total']}")
print(f"Rating moyen : {stats['avg_rating']:.2f}/5")
```

### Export Données

**SQLite → CSV** :
```bash
sqlite3 fact_checks.db <<EOF
.headers on
.mode csv
.output verifications.csv
SELECT * FROM checkpoints;
.quit
EOF
```

**Analyse avec Pandas** :
```python
import pandas as pd
import sqlite3

conn = sqlite3.connect('fact_checks.db')
df = pd.read_sql_query("SELECT * FROM checkpoints", conn)

# Top claims vérifiées
df['claim'].value_counts().head(10)

# Ratio verdicts
df['verdict'].value_counts(normalize=True)
```

---

**Développé avec ❤️ pour lutter contre la désinformation**

**Version** : 3.2.1 (Novembre 2024)  
**Statut** : ✅ Production-Ready
