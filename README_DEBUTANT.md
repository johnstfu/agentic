# 🔍 FACT-CHECKER AGENT - Guide Complet pour Débutants

**Version 2.0 - Système de scoring rigoureux avec esprit critique**

---

## 📚 Table des Matières

1. [Qu'est-ce que le Fact-Checker Agent ?](#quest-ce-que-le-fact-checker-agent-)
2. [Comment ça marche ?](#comment-ça-marche-)
3. [Installation Step-by-Step](#installation-step-by-step)
4. [Utilisation](#utilisation)
5. [Comprendre le Score de Confiance](#comprendre-le-score-de-confiance)
6. [Hiérarchie des Sources](#hiérarchie-des-sources)
7. [Ressources Pédagogiques](#ressources-pédagogiques)
8. [Architecture Technique](#architecture-technique)
9. [Dépannage](#dépannage)

---

## 🎯 Qu'est-ce que le Fact-Checker Agent ?

Le **Fact-Checker Agent** est une application web qui vérifie automatiquement la véracité d'affirmations en recherchant et analysant des **sources institutionnelles fiables**.

### Objectifs du Projet

1. **Vérifier les faits** : Confirmer ou infirmer des affirmations
2. **Évaluer les sources** : Distinguer sources fiables et non fiables
3. **Développer l'esprit critique** : Fournir des ressources pédagogiques

### Ce que l'outil fait

✅ Recherche automatique sur le web avec DuckDuckGo
✅ Analyse de la fiabilité des sources (gouvernement, scientifique, etc.)
✅ Calcul d'un score de confiance rigoureux
✅ Recommandations pédagogiques si score faible
✅ Export des résultats en JSON

### Ce que l'outil NE fait PAS

❌ N'utilise PAS d'intelligence artificielle OpenAI (coûteuse)
❌ Ne remplace PAS votre jugement personnel
❌ Ne garantit PAS une vérité absolue (mais indique la fiabilité)

---

## ⚙️ Comment ça marche ?

### 1️⃣ Recherche Web

L'application utilise **DuckDuckGo** pour rechercher l'affirmation sur Internet.

```
Affirmation : "La France a 67 millions d'habitants"
    ↓
Recherche : "La France a 67 millions d'habitants"
    ↓
Résultats : 10 URLs
```

### 2️⃣ Analyse des Sources

Chaque URL est analysée selon un **système de scoring institutionnel** :

| Score | Type de Source | Exemples |
|-------|----------------|----------|
| **10/10** | Gouvernement français | gouvernement.fr, insee.fr |
| **9/10** | Organisations internationales | who.int, un.org, europa.eu |
| **8/10** | Publications scientifiques | nature.com, pubmed.ncbi.nlm.nih.gov |
| **7/10** | Fact-checkers & encyclopédies | snopes.com, britannica.com |
| **6/10** | Médias de référence | reuters.com, bbc.com, lemonde.fr |
| **< 6/10** | Sources non vérifiées | Blogs, réseaux sociaux, etc. |

### 3️⃣ Calcul du Score de Confiance

**Algorithme rigoureux** :

```
SI ≥ 2 sources institutionnelles (score ≥ 8/10) :
    → ✅ VÉRIFIÉ (confiance : 65-95%)

SINON SI 1 source institutionnelle + ≥ 2 sources officielles :
    → ⚠️ PARTIELLEMENT VÉRIFIÉ (confiance : 50-75%)

SINON SI ≥ 1 source officielle + score moyen ≥ 0.5 :
    → ⚠️ PARTIELLEMENT VÉRIFIÉ (confiance : 35-65%)

SINON SI score moyen ≥ 0.35 :
    → ❓ DONNÉES INSUFFISANTES (confiance : 15-45%)

SINON :
    → ❌ NON VÉRIFIÉ (confiance : 5-20%)
```

### 4️⃣ Ressources Pédagogiques

**Si le score de confiance < 60%**, l'application propose automatiquement des articles officiels pour développer l'esprit critique :

- **Confiance < 30%** → Guides de base (gouvernement.fr, unesco.org)
- **Confiance 30-50%** → Méthodologie (CLEMI, INSERM)
- **Confiance 50-60%** → Approfondissement (CorteX, CheckNews)

---

## 🚀 Installation Step-by-Step

### Prérequis

- **Python 3.9+** installé sur votre machine
- **Terminal** (ou Invite de commandes sur Windows)
- **Connexion Internet**

### Étape 1 : Ouvrir le Terminal

**macOS/Linux** :
```bash
# Ouvrir le Terminal (Cmd+Espace → "Terminal")
cd /Users/rayanekryslak-medioub/Desktop/AlbertSchool1/Agentic/Cnews
```

**Windows** :
```bash
# Ouvrir l'Invite de commandes (Win+R → "cmd")
cd C:\Users\VotreNom\Desktop\AlbertSchool1\Agentic\Cnews
```

### Étape 2 : Vérifier Python

```bash
python3 --version
# Devrait afficher : Python 3.9.x ou supérieur
```

Si Python n'est pas installé :
- **macOS** : Installer avec Homebrew (`brew install python3`)
- **Windows** : Télécharger depuis https://www.python.org/downloads/
- **Linux** : `sudo apt install python3 python3-venv`

### Étape 3 : Créer l'Environnement Virtuel

```bash
python3 -m venv venv
```

**Explication** : Crée un dossier `venv` contenant Python et ses bibliothèques isolées.

### Étape 4 : Installer les Dépendances

```bash
./venv/bin/pip install streamlit plotly duckduckgo-search beautifulsoup4 requests python-dotenv
```

**Sur Windows** :
```bash
venv\Scripts\pip install streamlit plotly duckduckgo-search beautifulsoup4 requests python-dotenv
```

**Durée** : 2-3 minutes (dépend de votre connexion Internet)

### Étape 5 : Lancer l'Application

```bash
./venv/bin/python -m streamlit run streamlit_fact_checker.py --server.port 8501
```

**Sur Windows** :
```bash
venv\Scripts\python -m streamlit run streamlit_fact_checker.py --server.port 8501
```

### Étape 6 : Ouvrir dans le Navigateur

L'application s'ouvre automatiquement dans votre navigateur à l'adresse :

**http://localhost:8501**

Si ce n'est pas le cas, copiez-collez cette URL dans votre navigateur.

---

## 💡 Utilisation

### Mode 1 : Texte Libre

1. Dans la sidebar, sélectionnez **"Texte libre"**
2. Entrez une affirmation : `"La Tour Eiffel mesure 330 mètres"`
3. Cliquez sur **🔍 Vérifier**
4. Attendez l'analyse (5-10 secondes)
5. Consultez le verdict et les sources

### Mode 2 : Analyse d'URL

1. Sélectionnez **"URL/Article"**
2. Collez l'URL d'un article
3. Lisez l'aperçu du contenu extrait
4. Entrez l'affirmation spécifique à vérifier
5. Cliquez sur **🔍 Vérifier**

### Mode 3 : Recherche Avancée

1. Sélectionnez **"Recherche avancée"**
2. Entrez un sujet : `"population française 2024"`
3. Consultez les résultats de recherche
4. Formulez une affirmation à vérifier
5. Cliquez sur **🔍 Vérifier**

---

## 📊 Comprendre le Score de Confiance

### Interprétation des Scores

| Score | Signification | Action Recommandée |
|-------|---------------|---------------------|
| **80-95%** | ✅ Vérifié par sources institutionnelles | Confiance élevée |
| **60-79%** | ⚠️ Partiellement vérifié | Vérification supplémentaire conseillée |
| **40-59%** | ⚠️ Données insuffisantes | Chercher plus de sources |
| **20-39%** | ❓ Peu de sources fiables | Scepticisme recommandé |
| **< 20%** | ❌ Non vérifié | Ne pas partager sans vérification |

### Facteurs qui Influencent le Score

1. **Nombre de sources institutionnelles** (score ≥ 8/10)
   - 2+ sources → Score élevé
   - 1 source → Score moyen
   - 0 source → Score faible

2. **Qualité moyenne des sources**
   - Moyenne ≥ 0.7 → Bonus significatif
   - Moyenne < 0.4 → Pénalité

3. **Convergence des sources**
   - Sources indépendantes → Bonus
   - Une seule source → Pénalité

---

## 🏛️ Hiérarchie des Sources

### Niveau 10 : Institutions Gouvernementales Françaises

**Pourquoi le score maximal ?**
- Sources officielles de l'État français
- Données vérifiées et actualisées régulièrement
- Responsabilité juridique

**Exemples** :
- `gouvernement.fr` - Portail officiel du gouvernement
- `insee.fr` - Institut National de la Statistique
- `legifrance.gouv.fr` - Textes juridiques officiels
- `data.gouv.fr` - Données publiques

### Niveau 9 : Organisations Internationales

**Pourquoi un score élevé ?**
- Expertise mondiale reconnue
- Méthodes scientifiques rigoureuses
- Indépendance politique

**Exemples** :
- `who.int` - Organisation Mondiale de la Santé
- `un.org` - Organisation des Nations Unies
- `europa.eu` - Union Européenne
- `unesco.org` - UNESCO

### Niveau 8 : Publications Scientifiques

**Pourquoi un score élevé ?**
- Comité de lecture (peer-review)
- Rigueur méthodologique
- Reproductibilité des résultats

**Exemples** :
- `nature.com` - Nature (revue scientifique)
- `science.org` - Science Magazine
- `pubmed.ncbi.nlm.nih.gov` - Base de données médicales

### Niveau 7 : Fact-Checkers & Encyclopédies

**Pourquoi un bon score ?**
- Méthodologie de vérification transparente
- Sources multiples
- Corrections publiques si erreurs

**Exemples** :
- `snopes.com` - Fact-checking reconnu
- `lemonde.fr/les-decodeurs` - Les Décodeurs du Monde
- `britannica.com` - Encyclopédie Britannica

### Niveau 6 : Médias de Référence

**Pourquoi un score correct ?**
- Déontologie journalistique
- Vérification avant publication
- Corrections si nécessaires

**Exemples** :
- `reuters.com` - Agence Reuters
- `bbc.com` - BBC
- `lemonde.fr` - Le Monde

### Niveau < 6 : Sources Non Vérifiées

**Pourquoi un score faible ?**
- Pas de processus de vérification
- Biais possibles
- Absence de responsabilité éditoriale

**Exemples** :
- Blogs personnels
- Réseaux sociaux (sans contexte)
- Sites d'opinion

---

## 🧠 Ressources Pédagogiques

### Comment Développer Son Esprit Critique ?

L'application propose des ressources adaptées selon votre score :

#### Si Score < 30% : Bases de la Vérification

1. **🎓 Comment identifier une source fiable**
   - URL : `gouvernement.fr/comment-verifier-une-information`
   - Contenu : Guide officiel du gouvernement

2. **🔍 Les biais cognitifs**
   - URL : `unesco.org/fr/media-information-literacy`
   - Contenu : Éducation aux médias (UNESCO)

3. **⚠️ Reconnaître les fake news**
   - URL : `service-public.fr`
   - Contenu : Conseils pratiques

#### Si Score 30-50% : Approfondissement

4. **📚 Méthodologie de fact-checking**
   - URL : `lemonde.fr/les-decodeurs/`
   - Contenu : Fact-checking professionnel

5. **🧠 Esprit critique**
   - URL : `clemi.fr`
   - Contenu : Centre d'éducation aux médias

6. **🔬 Sciences vs pseudo-sciences**
   - URL : `inserm.fr`
   - Contenu : Publications scientifiques

#### Si Score 50-60% : Expertise

7. **📖 Hiérarchie des sources**
   - URL : `liberation.fr/checknews/`
   - Contenu : Vérifications de lecteurs

8. **🎯 Exercices pratiques**
   - URL : `cortecs.org`
   - Contenu : Esprit critique et sciences

---

## 🏗️ Architecture Technique

### Structure du Projet

```
Cnews/
├── streamlit_fact_checker.py    # Interface web (PRINCIPAL)
├── fact_checker_agent.py        # Agent LangChain (optionnel)
├── venv/                        # Environnement virtuel Python
├── .env                         # Configuration (ne PAS commit)
├── claims_examples.txt          # Exemples d'affirmations
├── requirements.txt             # Liste des dépendances
├── start.sh                     # Script de lancement (macOS/Linux)
└── README_DEBUTANT.md          # Ce fichier
```

### Fichiers Importants

#### `streamlit_fact_checker.py`

**Rôle** : Interface web principale

**Composants** :
- `TRUSTED_SOURCES` : Dictionnaire des sources fiables (lignes 93-137)
- `FactCheckerEngine` : Moteur de vérification (lignes 139-428)
  - `extract_content_from_url()` : Scraping HTML
  - `search_web()` : Recherche DuckDuckGo
  - `calculate_trust_score()` : Calcul du score d'une URL
  - `verify_claim()` : Algorithme principal de vérification
  - `_get_critical_thinking_resources()` : Ressources pédagogiques
- `main()` : Interface Streamlit (lignes 430-fin)

#### `fact_checker_agent.py`

**Rôle** : Agent IA avancé (nécessite OpenAI, **OPTIONNEL**)

**Utilisation** : Seulement si vous avez une clé API OpenAI

#### `.env`

**Rôle** : Configuration sensible

**Contenu** :
```
OPENAI_API_KEY=votre-cle-api-ici   # Optionnel, pour fact_checker_agent.py
```

### Technologies Utilisées

| Technologie | Rôle | Pourquoi ? |
|-------------|------|-----------|
| **Streamlit** | Interface web | Simple, rapide, Python natif |
| **DuckDuckGo Search** | Moteur de recherche | Gratuit, sans limite, respecte la vie privée |
| **BeautifulSoup** | Scraping HTML | Extraction du contenu des pages web |
| **Plotly** | Graphiques | Visualisation interactive des statistiques |
| **Python-dotenv** | Variables d'environnement | Sécurité (clés API) |

---

## 🛠️ Dépannage

### Problème : "command not found: python3"

**Solution** :
```bash
# macOS/Linux
brew install python3

# Windows
# Télécharger depuis https://www.python.org/downloads/
```

### Problème : "No module named streamlit"

**Cause** : Dépendances pas installées

**Solution** :
```bash
./venv/bin/pip install streamlit plotly duckduckgo-search beautifulsoup4 requests python-dotenv
```

### Problème : "Address already in use (port 8501)"

**Cause** : Streamlit déjà lancé sur ce port

**Solution 1** : Arrêter le processus existant
```bash
# macOS/Linux
lsof -ti:8501 | xargs kill -9

# Windows
netstat -ano | findstr :8501
taskkill /PID [PID] /F
```

**Solution 2** : Utiliser un autre port
```bash
./venv/bin/python -m streamlit run streamlit_fact_checker.py --server.port 8502
```

### Problème : "Erreur de recherche: ..."

**Cause** : DuckDuckGo temporairement indisponible ou rate-limit

**Solution** :
1. Attendre 1-2 minutes
2. Réessayer avec une autre formulation
3. Vérifier votre connexion Internet

### Problème : L'interface ne s'affiche pas

**Solution** :
1. Vérifier que Streamlit est bien lancé (voir messages dans le terminal)
2. Ouvrir manuellement http://localhost:8501 dans votre navigateur
3. Essayer un autre navigateur (Chrome, Firefox, Safari)
4. Vider le cache du navigateur (Cmd+Shift+R ou Ctrl+Shift+R)

---

## 🎓 Pour Aller Plus Loin

### Exercices Pratiques

1. **Exercice 1 : Vérifier une affirmation simple**
   - Affirmation : "La France a 67 millions d'habitants"
   - Objectif : Atteindre un score > 80%

2. **Exercice 2 : Analyser une fake news**
   - Affirmation : "Le vaccin COVID-19 contient des puces 5G"
   - Objectif : Comprendre pourquoi le score est faible

3. **Exercice 3 : Comparer les sources**
   - Comparez le score d'une affirmation avec et sans sources institutionnelles
   - Objectif : Comprendre l'importance de la qualité des sources

### Améliorations Possibles

- Ajouter plus de sources institutionnelles françaises
- Implémenter la détection automatique de la langue
- Ajouter un système de cache pour accélérer les requêtes
- Créer un historique des vérifications

---

## 📞 Support

### Ressources

- **Documentation Streamlit** : https://docs.streamlit.io/
- **Fact-checking FR** : https://www.lemonde.fr/les-decodeurs/
- **Esprit critique** : https://cortecs.org/

### Questions Fréquentes

**Q : L'outil peut-il vérifier des images ou vidéos ?**
R : Non, uniquement du texte pour l'instant.

**Q : Puis-je utiliser l'outil hors ligne ?**
R : Non, nécessite une connexion Internet pour la recherche web.

**Q : Les résultats sont-ils toujours fiables ?**
R : Non, l'outil fournit une indication de fiabilité basée sur les sources disponibles. Le jugement humain reste essentiel.

**Q : Puis-je ajouter mes propres sources fiables ?**
R : Oui ! Modifiez le dictionnaire `TRUSTED_SOURCES` dans `streamlit_fact_checker.py` (lignes 93-137).

---

**Développé avec rigueur scientifique et esprit critique 🧠**
**Version 2.0 - Octobre 2025**
