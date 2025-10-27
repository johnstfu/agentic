# 🔍 FACT-CHECKER INTELLIGENT - Tavily + OpenAI

**Architecture moderne de vérification automatique des faits**

## 🎯 **Fonctionnement**

### **1. Tavily (Recherche Web Avancée)** 🌐
- Cherche automatiquement les **meilleures sources** sur le web
- API de recherche optimisée pour le fact-checking
- Retourne titre, URL, contenu pertinent
- Génère une **synthèse automatique**

### **2. OpenAI (Analyse Intelligente)** 🤖
- Analyse les sources trouvées par Tavily
- Génère un **verdict intelligent** (VÉRIFIÉ / NON VÉRIFIÉ / INCERTAIN)
- Calcule un **score de véracité** (0-100%)
- Cite **explicitement les sources**

### **3. Streamlit (Interface Utilisateur)** 💻
- Interface web intuitive
- Affichage clair du verdict et des sources
- **Transparence totale** : logs de l'agent visibles
- Export des résultats en JSON

---

## 🚀 **Utilisation**

### **Lancement Rapide**
```bash
cd /Users/rayanekryslak-medioub/Desktop/AlbertSchool1/Agentic/Cnews
python3 -m streamlit run streamlit_fact_checker.py
```

### **Accès à l'interface**
**URL** : http://localhost:8501

---

## 📊 **Architecture Technique**

```
UTILISATEUR
    ↓
    Affirmation à vérifier
    ↓
TAVILY (Recherche Web)
    ↓
    5 meilleures sources + synthèse
    ↓
OPENAI (Analyse Intelligente)
    ↓
    Verdict + Score + Analyse détaillée
    ↓
STREAMLIT (Affichage)
    ↓
    Interface avec sources transparentes
```

---

## 🔑 **Configuration**

### **Fichier `.env` requis**
```env
# OpenAI (Analyse IA)
OPENAI_API_KEY=sk-proj-...

# Tavily (Recherche Web)
TAVILY_API_KEY=tvly-dev-...
```

---

## 🎯 **Exemples d'Utilisation**

### **Affirmations à Tester**
```
✅ VRAI:
- "La Tour Eiffel mesure 330 mètres de hauteur"
- "Emmanuel Macron est président de la France"
- "L'eau bout à 100°C au niveau de la mer"

❌ FAUX:
- "Le vaccin COVID-19 contient des puces 5G"
- "La Terre est plate"
- "Paris est la capitale de l'Espagne"

⚠️ INCERTAIN:
- Affirmations récentes sans sources fiables
- Sujets controversés avec sources contradictoires
```

---

## 📚 **Sources de Confiance**

L'agent **priorise automatiquement** :

### **🏛️ Gouvernement** (Score: 1.0/1.0)
- gouvernement.fr
- service-public.fr
- legifrance.gouv.fr

### **🏥 Santé Officielle** (Score: 0.95/1.0)
- who.int (OMS)
- inserm.fr
- pasteur.fr
- has-sante.fr

### **✅ Fact-Checkers** (Score: 0.9/1.0)
- afp.com / factuel.afp.com
- lemonde.fr/les-decodeurs
- liberation.fr/checknews

### **📰 Médias Fiables** (Score: 0.85/1.0)
- reuters.com
- bbc.com
- apnews.com

### **🔬 Scientifique** (Score: 0.9/1.0)
- nature.com
- science.org
- pubmed.ncbi.nlm.nih.gov

---

## 🧪 **Test Rapide**

```bash
# Test du système backend
python3 smart_fact_checker.py

# Résultat attendu:
# ✅ Tavily: 5 sources trouvées
# ✅ OpenAI: Verdict = ✅ VÉRIFIÉ, Score = 100%
```

---

## 📈 **Scoring de Véracité**

| Score | Verdict | Signification |
|-------|---------|---------------|
| **0-30%** | ❌ FAUX | Désinformation avérée - NE PAS partager |
| **31-69%** | ⚠️ INCERTAIN | Sources contradictoires - Vérifier davantage |
| **70-100%** | ✅ VRAI | Confirmé par sources fiables - Partageable |

---

## 🔒 **Sécurité et Confidentialité**

- ✅ **Pas de stockage** : Aucune donnée personnelle enregistrée
- ✅ **API sécurisées** : Clés dans `.env` (non versionné)
- ✅ **Sources vérifiées** : Priorité aux sources officielles
- ✅ **Transparence** : Logs et sources affichés

---

## 🛠️ **Dépendances**

```bash
pip install streamlit plotly python-dotenv
pip install langchain langchain-openai
pip install tavily-python
```

---

## 📊 **Exemple de Résultat**

```json
{
  "verdict": "✅ VÉRIFIÉ",
  "confidence": 95,
  "sources": [
    {
      "url": "https://www.toureiffel.paris/fr",
      "title": "Site officiel de la Tour Eiffel",
      "trust_score": 1.0,
      "ai_analysis": {
        "position": "CONFIRME",
        "confiance": 95
      }
    }
  ],
  "stats": {
    "total_sources": 5,
    "sources_confirment": 4,
    "sources_infirment": 0,
    "sources_institutionnelles": 2
  }
}
```

---

## 🎨 **Interface Streamlit**

### **Fonctionnalités**
- 📝 **Zone de saisie** : Entrez l'affirmation à vérifier
- 🎯 **Bouton de vérification** : Lance l'analyse
- 📊 **Score visuel** : Barre de progression colorée
- 📚 **Sources détaillées** : Chaque source avec son analyse IA
- 💾 **Export JSON** : Téléchargement des résultats
- 🔍 **Logs transparents** : Voir ce que l'agent a fait

---

## 🚨 **Troubleshooting**

### **Erreur : "OPENAI_API_KEY manquante"**
```bash
# Vérifier le fichier .env
cat .env

# Doit contenir:
OPENAI_API_KEY=sk-proj-...
```

### **Erreur : "TAVILY_API_KEY manquante"**
```bash
# Ajouter la clé Tavily dans .env
echo "TAVILY_API_KEY=tvly-dev-..." >> .env
```

### **Erreur : "Module tavily not found"**
```bash
pip install tavily-python
```

---

## 🎯 **Avantages de Tavily + OpenAI**

### **Tavily**
- ✅ Recherche web optimisée pour fact-checking
- ✅ Pas de problèmes 403 (API légale)
- ✅ Synthèse automatique des sources
- ✅ Rapide (4 secondes pour 5 sources)

### **OpenAI**
- ✅ Analyse intelligente et contextuelle
- ✅ Citations précises des sources
- ✅ Verdict nuancé (pas binaire)
- ✅ Explications claires et pédagogiques

### **Combinaison**
- 🚀 **Pipeline complet** : Recherche → Analyse → Verdict
- 🔍 **Transparence totale** : Sources + Logs visibles
- 🎯 **Précision** : Pondération des sources selon fiabilité
- 💡 **Intelligent** : Détecte les contradictions

---

## 📝 **Licence et Crédits**

**Développé avec** :
- 🌐 **Tavily** : API de recherche web avancée
- 🤖 **OpenAI GPT-4** : Analyse intelligente
- 💻 **Streamlit** : Interface web interactive
- 🐍 **Python 3.9+** : Backend robuste

**Fait avec ❤️ pour lutter contre la désinformation**

---

## 🔗 **Liens Utiles**

- [Documentation Tavily](https://tavily.com/docs)
- [OpenAI API](https://platform.openai.com/docs)
- [Streamlit](https://docs.streamlit.io)

---

**🚀 Interface opérationnelle sur http://localhost:8501**

**✅ Prêt à vérifier des affirmations avec Tavily + OpenAI !**
