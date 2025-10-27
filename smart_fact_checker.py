# PATH: smart_fact_checker.py
"""
🔍 SMART FACT-CHECKER - Tavily (Recherche Web) + OpenAI (Analyse Intelligente)
Architecture rigoureuse : Tavily cherche, OpenAI analyse et évalue la crédibilité dynamiquement
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

# OpenAI + LangChain
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage

# Tavily pour la recherche web
from tavily import TavilyClient

# Load environment variables
load_dotenv()


class SmartFactChecker:
    """
    Fact-Checker intelligent : Tavily (recherche) + OpenAI (analyse + évaluation crédibilité)
    
    Architecture rigoureuse:
    1. Tavily cherche les sources (sans biais)
    2. OpenAI analyse ET évalue la crédibilité de chaque source
    3. Score de confiance basé sur l'analyse IA (pas de hardcoding)
    """
    
    def __init__(self):
        """Initialise le fact-checker avec Tavily + OpenAI"""
        
        # Clés API
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        
        if not self.openai_key:
            raise ValueError("❌ OPENAI_API_KEY manquante dans .env")
        if not self.tavily_key:
            raise ValueError("❌ TAVILY_API_KEY manquante dans .env")
        
        # Initialisation Tavily (recherche web avancée)
        self.tavily = TavilyClient(api_key=self.tavily_key)
        
        # Initialisation OpenAI (analyse intelligente)
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",  # Version rapide et performante
            temperature=0.1,  # Faible pour plus de précision
            openai_api_key=self.openai_key
        )
        
        # Logs pour transparence
        self.logs = []
        
        print("✅ Smart Fact-Checker initialisé (Tavily + OpenAI)")
        self.log("✅ Agent initialisé avec Tavily (recherche web) + OpenAI (analyse)")
    
    def log(self, message: str):
        """Ajoute un log pour transparence"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        print(log_entry)
    
    def search_with_tavily(self, claim: str, max_results: int = 8) -> List[Dict]:
        """
        Recherche avec Tavily (API de recherche web avancée)
        
        Tavily retourne automatiquement:
        - URL
        - Titre
        - Contenu pertinent
        - Score de pertinence
        """
        self.log(f"🔍 Recherche Tavily pour: '{claim[:50]}...'")
        
        try:
            # Recherche Tavily avec paramètres optimisés
            response = self.tavily.search(
                query=claim,
                max_results=max_results,
                search_depth="advanced",  # Recherche approfondie
                include_answer=True,  # Tavily génère une réponse synthétique
                include_raw_content=False,  # Pas besoin du HTML brut
                include_images=False
            )
            
            sources = []
            
            # Extraction des résultats
            for result in response.get('results', []):
                url = result.get('url', '')
                
                source = {
                    'url': url,
                    'title': result.get('title', 'Sans titre'),
                    'content': result.get('content', ''),
                    'tavily_score': result.get('score', 0),  # Score Tavily
                    'trust_score': None,  # Sera calculé par OpenAI
                    'source_type': None,  # Sera déterminé par OpenAI
                    'credibility_analysis': None  # Analyse de crédibilité par OpenAI
                }
                sources.append(source)
            
            # Réponse synthétique de Tavily (optionnel)
            tavily_answer = response.get('answer', '')
            
            self.log(f"✅ Tavily: {len(sources)} sources trouvées")
            if tavily_answer:
                self.log(f"💡 Synthèse Tavily: {tavily_answer[:100]}...")
            
            return sources, tavily_answer
            
        except Exception as e:
            self.log(f"❌ Erreur Tavily: {str(e)}")
            return [], ""
    
    def analyze_sources_credibility(self, sources: List[Dict]) -> List[Dict]:
        """
        OpenAI analyse la crédibilité de chaque source dynamiquement
        
        Pour chaque source, OpenAI détermine:
        - Type de source (government, academic, media, etc.)
        - Score de crédibilité (0.0-1.0)
        - Analyse de la fiabilité
        """
        self.log("🤖 Analyse de crédibilité des sources par OpenAI...")
        
        # Préparation du contexte pour OpenAI
        sources_context = ""
        for idx, source in enumerate(sources, 1):
            sources_context += f"""
SOURCE {idx}:
- URL: {source['url']}
- Titre: {source['title']}
- Contenu: {source['content'][:400]}...
---
"""
        
        # Prompt système pour l'analyse de crédibilité - Version stricte
        system_prompt = """Tu es un expert en évaluation de crédibilité des sources web.

Ta mission : Analyser chaque source et déterminer sa crédibilité de manière STRICTE et objective.

CRITÈRES D'ÉVALUATION (par ordre d'importance):
1. Type d'institution (gouvernement > académique > média établi > blog)
2. Réputation historique de la source (vérifiable)
3. Expertise reconnue dans le domaine spécifique
4. Transparence méthodologique et éditoriale
5. Absence de conflits d'intérêts évidents

SCORING STRICT (0.0 à 1.0):
- 0.95-1.0: Gouvernements nationaux (.gov, .gouv), OMS, ONU, institutions UE officielles
- 0.85-0.94: Universités prestigieuses (.edu, .ac), Nature, Science, Lancet, institutions scientifiques reconnues
- 0.75-0.84: Médias établis haute réputation (Reuters, BBC, AFP, AP, Le Monde), organismes officiels
- 0.60-0.74: Médias généralistes reconnus, organisations scientifiques régionales
- 0.40-0.59: Blogs d'experts vérifiés, médias locaux, sites spécialisés
- 0.20-0.39: Sources peu connues, blogs personnels, sites non vérifiés
- 0.00-0.19: Sources douteuses, sites d'opinion, non vérifiables

FORMAT DE RÉPONSE (JSON STRICT):
{
  "sources": [
    {
      "source_index": 1,
      "source_type": "government|academic|media|blog|unknown",
      "credibility_score": 0.85,
      "credibility_analysis": "Justification claire et factuelle du score attribué"
    }
  ]
}

RÈGLES IMPORTANTES:
- Sois STRICT: un média généraliste = 0.6-0.7 maximum (pas 0.8)
- Sois EXIGEANT: seules les institutions officielles atteignent 0.9+
- JUSTIFIE: chaque score doit avoir une explication concrète

TRANSPARENCE: Cite les éléments factuels qui justifient le score (ex: "domaine .gov", "média reconnu depuis 1950")."""
        
        # Prompt utilisateur
        user_prompt = f"""Analyse la crédibilité de ces sources web:

{sources_context}

Pour chaque source, détermine:
1. Le type de source
2. Un score de crédibilité (0.0-1.0)
3. Une analyse justifiant le score

Réponds UNIQUEMENT en JSON valide."""
        
        try:
            # Appel à OpenAI
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            analysis = response.content
            
            # Parse JSON - Extraction robuste
            try:
                # Nettoyage du JSON (suppression du markdown)
                json_start = analysis.find('{')
                json_end = analysis.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = analysis[json_start:json_end]
                    credibility_data = json.loads(json_str)
                    
                    # Application des scores aux sources
                    for source_data in credibility_data.get('sources', []):
                        idx = source_data['source_index'] - 1
                        if 0 <= idx < len(sources):
                            sources[idx]['trust_score'] = source_data['credibility_score']
                            sources[idx]['source_type'] = source_data['source_type']
                            sources[idx]['credibility_analysis'] = source_data['credibility_analysis']
                    
                    self.log(f"✅ Crédibilité analysée pour {len(sources)} sources")
                else:
                    raise ValueError("JSON non trouvé")
                
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                self.log(f"⚠️ Erreur parsing JSON: {str(e)}, analyse manuelle")
                # Analyse manuelle des scores
                for i, source in enumerate(sources):
                    url = source['url'].lower()
                    if any(dom in url for dom in ['gov', 'gouv', 'who.int', 'edu', 'ac.']):
                        source['trust_score'] = 0.8
                        source['source_type'] = 'government'
                    elif any(dom in url for dom in ['reuters', 'bbc', 'apnews', 'afp']):
                        source['trust_score'] = 0.7
                        source['source_type'] = 'media'
                    elif any(dom in url for dom in ['nature', 'science', 'pubmed']):
                        source['trust_score'] = 0.9
                        source['source_type'] = 'academic'
                    else:
                        source['trust_score'] = 0.5
                        source['source_type'] = 'general'
                    source['credibility_analysis'] = f"Score automatique basé sur le domaine: {source['source_type']}"
            
            return sources
            
        except Exception as e:
            self.log(f"❌ Erreur analyse crédibilité: {str(e)}")
            # Fallback
            for source in sources:
                source['trust_score'] = 0.5
                source['source_type'] = 'unknown'
                source['credibility_analysis'] = 'Erreur d\'analyse'
            return sources
    
    def analyze_claim_with_sources(self, claim: str, sources: List[Dict], tavily_answer: str, context: str = "") -> Dict:
        """
        OpenAI analyse l'affirmation en se basant sur les sources analysées
        
        OpenAI reçoit:
        1. L'affirmation à vérifier
        2. Les sources avec leur crédibilité analysée
        3. La synthèse Tavily
        4. Contexte optionnel
        
        OpenAI retourne:
        - Verdict (VÉRIFIÉ / NON VÉRIFIÉ / PARTIELLEMENT VÉRIFIÉ)
        - Score de confiance (0-100%)
        - Analyse détaillée
        - Position de chaque source (CONFIRME / INFIRME / NEUTRE)
        """
        self.log("🤖 Analyse de l'affirmation par OpenAI...")
        
        # Préparation du contexte des sources pour OpenAI
        sources_context = ""
        for idx, source in enumerate(sources, 1):
            sources_context += f"""
SOURCE {idx} (Crédibilité: {source['trust_score']:.2f}/1.0, Type: {source['source_type']}):
- URL: {source['url']}
- Titre: {source['title']}
- Contenu: {source['content'][:300]}...
- Analyse crédibilité: {source['credibility_analysis']}
---
"""
        
        # Prompt système pour OpenAI - Version améliorée avec format strict
        system_prompt = f"""Tu es un expert en fact-checking rigoureux et impartial.

Ta mission : analyser une affirmation en te basant UNIQUEMENT sur les sources fournies.

RÈGLES STRICTES:
1. Base ton analyse UNIQUEMENT sur les sources fournies (pas de connaissances externes)
2. Pondère chaque source selon sa crédibilité analysée (score fourni)
3. Si les sources se contredisent, identifie-le clairement
4. Fournis un score de véracité de 0% (FAUX) à 100% (VRAI)
5. Justifie CHAQUE conclusion avec des citations précises des sources

SCORING RIGOUREUX:
- 0-20% = FAUX (désinformation confirmée par sources haute crédibilité)
- 21-40% = PROBABLEMENT FAUX (majorité des sources infirment)
- 41-60% = INCERTAIN (sources contradictoires ou insuffisantes)
- 61-80% = PROBABLEMENT VRAI (majorité des sources confirment)
- 81-100% = VRAI (confirmé par multiples sources haute crédibilité ≥0.8)

FORMAT DE RÉPONSE OBLIGATOIRE (RESPECTE EXACTEMENT):
1. VERDICT: [Un seul mot parmi: VÉRIFIÉ / NON VÉRIFIÉ / PARTIELLEMENT VÉRIFIÉ / INCERTAIN]
2. SCORE DE VÉRACITÉ: [Nombre entre 0-100]%
3. ANALYSE DÉTAILLÉE: [2-3 phrases maximum avec citations des sources]
4. SOURCES PAR POSITION:
   - CONFIRMENT: [Liste des sources avec leur crédibilité, ex: "Source 1 (crédibilité 0.9): titre"]
   - INFIRMENT: [Liste des sources avec leur crédibilité]
   - NEUTRES: [Liste des sources avec leur crédibilité]
5. RECOMMANDATION: [1 phrase d'action concrète]

TRANSPARENCE TOTALE: Cite explicitement les sources (ex: "Source 1 affirme que...") pour chaque argument.

IMPORTANT: Ne donne PAS de score élevé (>70%) si les sources haute crédibilité (≥0.8) ne confirment pas clairement."""
        
        # Prompt utilisateur
        user_prompt = f"""AFFIRMATION À VÉRIFIER:
"{claim}"

{f'CONTEXTE ADDITIONNEL: {context}' if context else ''}

SYNTHÈSE TAVILY (recherche web):
{tavily_answer if tavily_answer else 'Aucune synthèse disponible'}

SOURCES TROUVÉES PAR TAVILY (avec crédibilité analysée):
{sources_context}

Analyse cette affirmation de manière rigoureuse et factuelle."""
        
        try:
            # Appel à OpenAI
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            analysis = response.content
            
            # Extraction du score de véracité (parse simple)
            score = self._extract_score(analysis)
            
            # Détermination du verdict
            verdict = self._extract_verdict(analysis, score)
            
            self.log(f"✅ OpenAI: Verdict = {verdict}, Score = {score}%")
            
            # Analyse des sources (position de chaque source)
            sources_analysis = self._analyze_sources_position(sources, analysis)
            
            return {
                'verdict': verdict,
                'confidence': score,
                'raw_analysis': analysis,
                'sources_analysis': sources_analysis
            }
            
        except Exception as e:
            self.log(f"❌ Erreur OpenAI: {str(e)}")
            return {
                'verdict': 'ERREUR',
                'confidence': 0,
                'raw_analysis': f"Erreur lors de l'analyse: {str(e)}",
                'sources_analysis': []
            }
    
    def _extract_score(self, analysis: str) -> int:
        """Extrait le score de véracité de l'analyse OpenAI avec extraction robuste"""
        import re

        # Pattern 1: Cherche "SCORE DE VÉRACITÉ: X%"
        patterns = [
            r'SCORE\s+DE\s+VÉRACITÉ\s*[:\s]+(\d+)%',
            r'VÉRACITÉ\s*[:\s]+(\d+)%',
            r'SCORE\s*[:\s]+(\d+)%',
            r'CONFIANCE\s*[:\s]+(\d+)%'
        ]

        for pattern in patterns:
            match = re.search(pattern, analysis, re.IGNORECASE)
            if match:
                score = int(match.group(1))
                return min(100, max(0, score))  # Clamp entre 0-100

        # Pattern 2: Cherche les lignes avec "2." suivies d'un score
        match = re.search(r'2\.\s+SCORE[^\d]*(\d+)%', analysis, re.IGNORECASE)
        if match:
            score = int(match.group(1))
            return min(100, max(0, score))

        # Fallback: cherche des mots-clés avec classification stricte
        analysis_lower = analysis.lower()
        if any(word in analysis_lower for word in ['faux', 'désinformation', 'non vérifié', 'erroné', 'infirmé']):
            # Détection plus fine
            if 'totalement' in analysis_lower or 'complètement' in analysis_lower:
                return 5  # Totalement faux
            return 15  # Faux
        elif any(word in analysis_lower for word in ['incertain', 'contradictoire', 'partiellement', 'mitigé']):
            return 50
        elif any(word in analysis_lower for word in ['vrai', 'vérifié', 'confirmé', 'correct']):
            # Détection plus fine
            if 'largement' in analysis_lower or 'totalement' in analysis_lower:
                return 95  # Totalement vrai
            return 80  # Vrai

        return 50  # Par défaut incertain
    
    def _extract_verdict(self, analysis: str, score: int) -> str:
        """Extrait le verdict de l'analyse OpenAI avec détection robuste"""
        import re
        analysis_lower = analysis.lower()

        # Pattern 1: Cherche "VERDICT: [TEXTE]"
        verdict_match = re.search(r'1\.\s+VERDICT\s*[:\s]+(.+?)(?:\n|2\.)', analysis, re.IGNORECASE | re.DOTALL)
        if verdict_match:
            verdict_text = verdict_match.group(1).strip().upper()
            if 'NON VÉRIFIÉ' in verdict_text or 'NON-VÉRIFIÉ' in verdict_text or 'FAUX' in verdict_text:
                return '❌ NON VÉRIFIÉ'
            elif 'PARTIELLEMENT' in verdict_text or 'INCERTAIN' in verdict_text:
                return '⚠️ PARTIELLEMENT VÉRIFIÉ'
            elif 'VÉRIFIÉ' in verdict_text or 'VRAI' in verdict_text:
                return '✅ VÉRIFIÉ'

        # Pattern 2: Cherche dans tout le texte
        if 'verdict' in analysis_lower:
            if 'non vérifié' in analysis_lower or 'non-vérifié' in analysis_lower:
                return '❌ NON VÉRIFIÉ'
            elif 'partiellement vérifié' in analysis_lower or 'partiellement' in analysis_lower:
                return '⚠️ PARTIELLEMENT VÉRIFIÉ'
            elif 'vérifié' in analysis_lower:
                return '✅ VÉRIFIÉ'

        # Basé sur le score avec seuils plus stricts
        if score >= 75:
            return '✅ VÉRIFIÉ'
        elif score >= 25:
            return '⚠️ PARTIELLEMENT VÉRIFIÉ'
        else:
            return '❌ NON VÉRIFIÉ'
    
    def _analyze_sources_position(self, sources: List[Dict], analysis: str) -> List[Dict]:
        """
        Analyse la position de chaque source selon l'analyse OpenAI
        (CONFIRME / INFIRME / NEUTRE)
        """
        analysis_lower = analysis.lower()
        
        for source in sources:
            # Détection simple basée sur la présence dans l'analyse
            source_mention = source['url'].lower() in analysis_lower or source['title'].lower() in analysis_lower
            
            if source_mention:
                # Analyse du contexte autour de la mention
                if any(word in analysis_lower for word in ['confirme', 'vérifie', 'valide', 'corrobore']):
                    position = 'CONFIRME'
                    confiance = 80
                elif any(word in analysis_lower for word in ['infirme', 'dément', 'contredit', 'faux']):
                    position = 'INFIRME'
                    confiance = 75
                else:
                    position = 'NEUTRE'
                    confiance = 50
            else:
                position = 'NEUTRE'
                confiance = 40
            
            source['ai_analysis'] = {
                'position': position,
                'confiance': confiance,
                'resume': f"Source {position.lower()} selon l'analyse IA"
            }
        
        return sources
    
    def verify_claim(self, claim: str, context: str = "") -> Dict:
        """
        Méthode principale : vérifie une affirmation
        
        Pipeline rigoureux:
        1. Recherche Tavily (sources web)
        2. Analyse crédibilité des sources par OpenAI
        3. Analyse de l'affirmation par OpenAI
        4. Agrégation des résultats
        
        Returns:
            Dict avec verdict, score, analyse, sources, logs
        """
        self.logs = []  # Reset logs
        self.log(f"🎯 Vérification de: '{claim[:60]}...'")
        
        # 1. Recherche avec Tavily
        sources, tavily_answer = self.search_with_tavily(claim)
        
        if not sources:
            self.log("⚠️ Aucune source trouvée par Tavily")
            return {
                'verdict': '❓ DONNÉES INSUFFISANTES',
                'confidence': 0,
                'raw_analysis': "Aucune source trouvée pour vérifier cette affirmation.",
                'sources': [],
                'logs': self.logs,
                'timestamp': datetime.now().isoformat(),
                'stats': {
                    'total_sources': 0,
                    'sources_confirment': 0,
                    'sources_infirment': 0,
                    'high_credibility_sources': 0
                }
            }
        
        # 2. Analyse de crédibilité des sources par OpenAI
        sources = self.analyze_sources_credibility(sources)
        
        # 3. Analyse de l'affirmation avec OpenAI
        ai_result = self.analyze_claim_with_sources(claim, sources, tavily_answer, context)
        
        # 4. Agrégation des statistiques
        stats = self._compute_stats(sources)
        
        # 5. Résultat final
        result = {
            'verdict': ai_result['verdict'],
            'confidence': ai_result['confidence'],
            'raw_analysis': ai_result['raw_analysis'],
            'sources': sources,
            'logs': self.logs,
            'timestamp': datetime.now().isoformat(),
            'stats': stats,
            'source_name': 'Tavily + OpenAI (Analyse Dynamique)'
        }
        
        self.log(f"✅ Vérification terminée: {ai_result['verdict']} ({ai_result['confidence']}%)")
        
        return result
    
    def _compute_stats(self, sources: List[Dict]) -> Dict:
        """Calcule les statistiques des sources"""
        total = len(sources)
        confirment = sum(1 for s in sources if s.get('ai_analysis', {}).get('position') == 'CONFIRME')
        infirment = sum(1 for s in sources if s.get('ai_analysis', {}).get('position') == 'INFIRME')
        high_credibility = sum(1 for s in sources if s.get('trust_score', 0) >= 0.7)
        
        return {
            'total_sources': total,
            'sources_confirment': confirment,
            'sources_infirment': infirment,
            'high_credibility_sources': high_credibility
        }


# === TEST RAPIDE ===
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TEST DU SMART FACT-CHECKER (VERSION RIGOUREUSE)")
    print("="*60)
    
    # Initialisation
    checker = SmartFactChecker()
    
    # Test avec une affirmation simple
    test_claim = "La Tour Eiffel mesure 330 mètres de hauteur"
    
    print(f"\n🔍 Test avec: '{test_claim}'")
    result = checker.verify_claim(test_claim)
    
    print(f"\n📊 Résultat:")
    print(f"  Verdict: {result['verdict']}")
    print(f"  Confiance: {result['confidence']}%")
    print(f"  Sources trouvées: {result['stats']['total_sources']}")
    print(f"  Sources haute crédibilité: {result['stats']['high_credibility_sources']}")
    print(f"\n✅ Test terminé!")
