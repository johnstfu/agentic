# 🎯 GUIDE D'UTILISATION - Fact-Checker Agent

**Version 2.0 - Guide Rapide**

---

## ⚡ Démarrage Rapide

```bash
cd /Users/rayanekryslak-medioub/Desktop/AlbertSchool1/Agentic/Cnews
./start.sh
```

**URL** : http://localhost:8501

---

## 📋 3 Modes d'Utilisation

### 🔹 Mode 1 : TEXTE LIBRE

**Pour** : Vérifier une affirmation textuelle

**Exemple** :
```
Affirmation : "La France a 67 millions d'habitants en 2024"
```

**ATTENTION** :
- ❌ Ne PAS mettre d'URL ici
- ✅ Phrase affirmative complète (minimum 10 caractères)

**Résultat attendu** : Sources trouvées, score de confiance calculé

---

### 🔹 Mode 2 : URL/ARTICLE

**Pour** : Analyser un article de presse complet

**Étape 1** : Coller l'URL
```
URL : https://www.franceinfo.fr/faits-divers/affaire-gregory-...
```

**Étape 2** : Lire l'aperçu du contenu extrait

**Étape 3** : Identifier UNE affirmation spécifique
```
Affirmation : "Jacqueline Jacob est mise en examen"
```

**Étape 4** : Cliquer sur "Vérifier"

**ATTENTION** :
- Le mode URL extrait le contenu PUIS vous demande une affirmation
- Ne pas reverifier l'URL elle-même

---

### 🔹 Mode 3 : RECHERCHE AVANCÉE

**Pour** : Explorer un sujet puis vérifier

**Étape 1** : Rechercher
```
Requête : "population française 2024"
```

**Étape 2** : Consulter les résultats

**Étape 3** : Formuler une affirmation
```
Affirmation : "La population française dépasse 68 millions"
```

---

## ✅ Exemples de Bonnes Affirmations

| ✅ BON | ❌ MAUVAIS |
|--------|------------|
| "La Tour Eiffel mesure 330 mètres" | "Tour Eiffel" (trop court) |
| "L'eau bout à 100°C au niveau de la mer" | "https://wikipedia.org/..." (URL) |
| "Emmanuel Macron est président en 2024" | "Macron ???" (vague) |
| "Le COVID-19 est causé par un virus" | "covid" (incomplet) |

---

## 🎯 Interpréter les Résultats

### Score de Confiance

| Score | Verdict | Action |
|-------|---------|--------|
| **80-95%** | ✅ VÉRIFIÉ | Confiance élevée |
| **60-79%** | ⚠️ PARTIELLEMENT VÉRIFIÉ | Vérifier davantage |
| **40-59%** | ⚠️ DONNÉES INSUFFISANTES | Scepticisme |
| **20-39%** | ❓ SOURCES PEU FIABLES | Méfiance |
| **< 20%** | ❌ NON VÉRIFIÉ | Ne pas partager |

### Sources par Niveau

- **🏛️ Niveau 10** : Gouvernement FR (insee.fr, gouvernement.fr)
- **🌍 Niveau 9** : ONU, OMS, UE
- **🔬 Niveau 8** : Nature, PubMed, Lancet
- **📊 Niveau 7** : Snopes, Décodeurs, Britannica
- **📰 Niveau 6** : Reuters, BBC, Le Monde
- **❓ < 6** : Sources non vérifiées

---

## 🧠 Ressources Pédagogiques

**Si score < 60%**, l'outil propose automatiquement :

- **< 30%** → Guides de base (gouvernement.fr, UNESCO)
- **30-50%** → Méthodologie (CLEMI, INSERM)
- **50-60%** → Approfondissement (CorteX, CheckNews)

---

## ⚠️ Erreurs Fréquentes

### Erreur 1 : URL en mode Texte Libre

❌ **ERREUR** :
```
Mode : Texte libre
Affirmation : "https://www.lemonde.fr/article..."
```

✅ **CORRECTION** :
```
Mode : URL/Article
URL : "https://www.lemonde.fr/article..."
```

### Erreur 2 : Affirmation Trop Courte

❌ **ERREUR** :
```
Affirmation : "Macron"
```

✅ **CORRECTION** :
```
Affirmation : "Emmanuel Macron est président de la France depuis 2017"
```

### Erreur 3 : Affirmation Vague

❌ **ERREUR** :
```
Affirmation : "C'est vrai ?"
```

✅ **CORRECTION** :
```
Affirmation : "Le vaccin contre la grippe réduit le risque de complications"
```

---

## 🚀 Workflow Recommandé

### Cas d'Usage 1 : Vérifier une Info Reçue

1. Passer en mode **"Texte libre"**
2. Copier l'affirmation exacte
3. Cliquer sur **"Vérifier"**
4. Consulter le score et les sources
5. Si score < 60%, lire les ressources pédagogiques

### Cas d'Usage 2 : Analyser un Article

1. Passer en mode **"URL/Article"**
2. Coller l'URL de l'article
3. Lire l'aperçu du contenu
4. Identifier l'affirmation principale
5. La copier dans le champ "Affirmation spécifique"
6. Vérifier

### Cas d'Usage 3 : Recherche Approfondie

1. Passer en mode **"Recherche avancée"**
2. Rechercher le sujet
3. Consulter les URLs trouvées
4. Formuler une affirmation précise
5. Vérifier

---

## 📊 Statistiques Avancées

Après vérification, cliquer sur **"📊 Voir les statistiques"** pour :

- Nombre total de sources analysées
- Nombre de sources officielles
- Score moyen de fiabilité
- Distribution des types de sources (graphique)

---

## 💾 Export des Résultats

Cliquer sur **"💾 Exporter les résultats"** → Télécharge un fichier JSON avec :

```json
{
  "claim": "La France a 67 millions d'habitants",
  "verdict": "✅ VÉRIFIÉ",
  "confidence": 92,
  "sources": [...],
  "institutional_sources": [...],
  "timestamp": "2025-10-24T11:30:00"
}
```

---

## 🔧 Paramètres Avancés

### Sidebar Configuration

- **Nombre max de sources** : 3-10 (recommandé : 5-8)
- **Confiance minimale** : 0-100% (recommandé : 50%)
- **Types de sources prioritaires** : government, scientific (recommandé)

---

## ❓ FAQ

**Q : Pourquoi "Aucune source trouvée" ?**
R : Affirmation trop spécifique, mal formulée, ou pas sur Internet

**Q : Pourquoi le score est faible ?**
R : Manque de sources institutionnelles fiables

**Q : Puis-je faire confiance à 100% ?**
R : NON. L'outil aide mais ne remplace pas votre jugement

**Q : Comment améliorer mon score ?**
R : Reformuler l'affirmation de manière plus factuelle et vérifiable

---

**Développé avec rigueur scientifique - Version 2.0**
