"""
Verdict generation logic - extracted from fact_checker.py
"""

import re
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.logger import FactCheckerLogger


def generate_verdict(claim: str, sources: List[Dict], tavily_answer: str, llm: ChatOpenAI, logger: FactCheckerLogger = None) -> Dict:
    """
    Generate verdict for a claim based on sources
    
    Args:
        claim: The claim to verify
        sources: List of analyzed sources
        tavily_answer: Tavily's answer summary
        llm: ChatOpenAI instance
        logger: Optional logger instance
        
    Returns:
        Dict with verdict, confidence, analysis, and sources_analysis
    """
    if logger is None:
        logger = FactCheckerLogger()
    
    logger.log("🤖 Analyse de l'affirmation...")
    
    sources_context = ""
    for idx, source in enumerate(sources, 1):
        sources_context += f"""
SOURCE {idx} (Crédibilité: {source['trust_score']:.2f}/1.0, Type: {source['source_type']}):
- URL: {source['url']}
- Titre: {source['title']}
- Contenu: {source['content'][:300]}...
- Analyse: {source['credibility_analysis']}
---
"""
    
    system_prompt = """Tu es un expert fact-checking rigoureux.

⚠️ DÉFINITIONS CRITIQUES - LIS ATTENTIVEMENT:

**VERDICTS POSSIBLES (ATTENTION À LA SIGNIFICATION):**
- ✅ VÉRIFIÉ : L'affirmation est VRAIE et confirmée par les sources
- ❌ NON VÉRIFIÉ : L'affirmation est FAUSSE ou contredite par les sources  
- ⚠️ PARTIELLEMENT VÉRIFIÉ : Une partie est vraie, une partie est fausse
- 🔍 INCERTAIN : Pas assez d'informations pour conclure

**SCORE DE VÉRACITÉ (importance: 0% = FAUX, 100% = VRAI):**
- 0-20%: FAUX total (désinformation) → VERDICT: ❌ NON VÉRIFIÉ
- 21-40%: PROBABLEMENT FAUX → VERDICT: ❌ NON VÉRIFIÉ
- 41-60%: INCERTAIN → VERDICT: 🔍 INCERTAIN
- 61-80%: PROBABLEMENT VRAI → VERDICT: ⚠️ PARTIELLEMENT VÉRIFIÉ
- 81-100%: VRAI confirmé → VERDICT: ✅ VÉRIFIÉ

🚨 RÈGLE D'OR ABSOLUE:
- Si l'affirmation est FAUSSE → Score 0-40% → Verdict "❌ NON VÉRIFIÉ"
- Si l'affirmation est VRAIE → Score 81-100% → Verdict "✅ VÉRIFIÉ"
- NE DIS JAMAIS "✅ VÉRIFIÉ" pour une affirmation FAUSSE !
- NE DIS JAMAIS "❌ NON VÉRIFIÉ" pour une affirmation VRAIE !

**EXEMPLE CORRECT:**
Affirmation: "La tour Eiffel est à Lyon"
→ Toutes les sources disent qu'elle est à Paris
→ Score: 0% (totalement faux)
→ Verdict: ❌ NON VÉRIFIÉ
→ Analyse: "L'affirmation est fausse. Les sources officielles confirment que la tour Eiffel est située à Paris, 7e arrondissement."

**EXEMPLE INCORRECT À ÉVITER:**
Affirmation: "La tour Eiffel est à Lyon"
→ Score: 100%
→ Verdict: ✅ VÉRIFIÉ  ← ERREUR GRAVE! Ne jamais dire VÉRIFIÉ pour du faux!

RÈGLES D'ANALYSE:
1. Base ton analyse UNIQUEMENT sur les sources fournies
2. Pondère selon la crédibilité (score ≥0.8 = très fiable)
3. Identifie les contradictions entre sources
4. Privilégie les sources haute crédibilité en cas de désaccord

FORMAT OBLIGATOIRE:
1. VERDICT: [✅ VÉRIFIÉ / ❌ NON VÉRIFIÉ / ⚠️ PARTIELLEMENT VÉRIFIÉ / 🔍 INCERTAIN]
2. SCORE DE VÉRACITÉ: [0-100]% (0% = totalement faux, 100% = totalement vrai)
3. ANALYSE DÉTAILLÉE: [2-3 phrases expliquant POURQUOI ce verdict, avec citations]
4. SOURCES PAR POSITION (INDIQUE LES NUMÉROS):
   - CONFIRMENT L'AFFIRMATION: SOURCE 1, SOURCE 3
   - INFIRMENT L'AFFIRMATION: SOURCE 2, SOURCE 4
   - NEUTRES: SOURCE 5
5. RECOMMANDATION: [1 phrase sur la fiabilité globale]

IMPORTANT: Classe chaque source explicitement selon qu'elle CONFIRME ou INFIRME l'affirmation."""
    
    user_prompt = f"""AFFIRMATION: "{claim}"

SYNTHÈSE TAVILY: {tavily_answer if tavily_answer else 'N/A'}

SOURCES:
{sources_context}

Analyse cette affirmation."""
    
    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = llm.invoke(messages)
        analysis = response.content
        
        score = _extract_score(analysis)
        verdict = _extract_verdict(analysis, score)
        sources_analysis = _analyze_sources_position(sources, analysis)
        
        logger.log(f"✅ Verdict: {verdict}, Score: {score}%")
        
        return {
            'verdict': verdict,
            'confidence': score,
            'raw_analysis': analysis,
            'sources_analysis': sources_analysis
        }
    
    except Exception as e:
        logger.log(f"❌ Erreur analyse: {str(e)}", "ERROR")
        return {
            'verdict': 'ERREUR',
            'confidence': 0,
            'raw_analysis': f"Erreur: {str(e)}",
            'sources_analysis': []
        }


def _extract_score(analysis: str) -> int:
    """Extract veracity score from analysis"""
    patterns = [
        r'SCORE\s+DE\s+VÉRACITÉ\s*[:\s]+(\d+)%',
        r'VÉRACITÉ\s*[:\s]+(\d+)%',
        r'SCORE\s*[:\s]+(\d+)%',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, analysis, re.IGNORECASE)
        if match:
            return min(100, max(0, int(match.group(1))))
    
    # Fallback based on keywords
    analysis_lower = analysis.lower()
    if any(word in analysis_lower for word in ['faux', 'désinformation', 'non vérifié']):
        return 15
    elif any(word in analysis_lower for word in ['incertain', 'contradictoire']):
        return 50
    elif any(word in analysis_lower for word in ['vrai', 'vérifié', 'confirmé']):
        return 85
    
    return 50


def _extract_verdict(analysis: str, score: int) -> str:
    """Extract verdict from analysis"""
    analysis_lower = analysis.lower()
    
    verdict_match = re.search(r'1\.\s+VERDICT\s*[:\s]+(.+?)(?:\n|2\.)', analysis, re.IGNORECASE | re.DOTALL)
    if verdict_match:
        verdict_text = verdict_match.group(1).strip().upper()
        if 'NON VÉRIFIÉ' in verdict_text or 'FAUX' in verdict_text:
            return '❌ NON VÉRIFIÉ'
        elif 'PARTIELLEMENT' in verdict_text or 'INCERTAIN' in verdict_text:
            return '⚠️ PARTIELLEMENT VÉRIFIÉ'
        elif 'VÉRIFIÉ' in verdict_text or 'VRAI' in verdict_text:
            return '✅ VÉRIFIÉ'
    
    # Based on score
    if score >= 75:
        return '✅ VÉRIFIÉ'
    elif score >= 25:
        return '⚠️ PARTIELLEMENT VÉRIFIÉ'
    else:
        return '❌ NON VÉRIFIÉ'


def _analyze_sources_position(sources: List[Dict], analysis: str) -> List[Dict]:
    """Analyze position of each source by parsing the SOURCES PAR POSITION section"""
    
    # Extract the "SOURCES PAR POSITION" section
    sources_section_match = re.search(
        r'4\.\s+SOURCES PAR POSITION[:\s]+(.+?)(?:5\.|$)', 
        analysis, 
        re.IGNORECASE | re.DOTALL
    )
    
    # Initialize all sources as NEUTRE by default
    for idx, source in enumerate(sources, 1):
        source['ai_analysis'] = {
            'position': 'NEUTRE',
            'confiance': 40,
            'resume': f"Source non classée"
        }
    
    if not sources_section_match:
        # Fallback: try to guess from keywords in full analysis
        analysis_lower = analysis.lower()
        for idx, source in enumerate(sources, 1):
            # Check if source number is mentioned with keywords
            source_ref = f"source {idx}"
            if source_ref in analysis_lower:
                context_around = analysis_lower[max(0, analysis_lower.find(source_ref)-100):analysis_lower.find(source_ref)+100]
                
                if any(word in context_around for word in ['confirme', 'vérifie', 'valide', 'corrobore', 'soutient']):
                    sources[idx-1]['ai_analysis'] = {
                        'position': 'CONFIRME',
                        'confiance': 75,
                        'resume': f"Source confirme l'affirmation"
                    }
                elif any(word in context_around for word in ['infirme', 'dément', 'contredit', 'faux', 'incorrect']):
                    sources[idx-1]['ai_analysis'] = {
                        'position': 'INFIRME',
                        'confiance': 75,
                        'resume': f"Source contredit l'affirmation"
                    }
        return sources
    
    # Parse the structured section
    sources_text = sources_section_match.group(1)
    
    # Extract CONFIRMENT
    confirment_match = re.search(r'CONFIRMENT[:\s]+(.+?)(?:INFIRMENT|NEUTRES|$)', sources_text, re.IGNORECASE | re.DOTALL)
    if confirment_match:
        confirment_text = confirment_match.group(1)
        # Extract source numbers (SOURCE 1, SOURCE 3, etc.)
        source_nums = re.findall(r'SOURCE\s+(\d+)', confirment_text, re.IGNORECASE)
        for num in source_nums:
            idx = int(num) - 1
            if 0 <= idx < len(sources):
                sources[idx]['ai_analysis'] = {
                    'position': 'CONFIRME',
                    'confiance': 85,
                    'resume': f"Source confirme l'affirmation"
                }
    
    # Extract INFIRMENT
    infirment_match = re.search(r'INFIRMENT[:\s]+(.+?)(?:NEUTRES|$)', sources_text, re.IGNORECASE | re.DOTALL)
    if infirment_match:
        infirment_text = infirment_match.group(1)
        source_nums = re.findall(r'SOURCE\s+(\d+)', infirment_text, re.IGNORECASE)
        for num in source_nums:
            idx = int(num) - 1
            if 0 <= idx < len(sources):
                sources[idx]['ai_analysis'] = {
                    'position': 'INFIRME',
                    'confiance': 85,
                    'resume': f"Source contredit l'affirmation"
                }
    
    # Extract NEUTRES
    neutres_match = re.search(r'NEUTRES[:\s]+(.+?)(?:$|\n\n|5\.)', sources_text, re.IGNORECASE | re.DOTALL)
    if neutres_match:
        neutres_text = neutres_match.group(1)
        source_nums = re.findall(r'SOURCE\s+(\d+)', neutres_text, re.IGNORECASE)
        for num in source_nums:
            idx = int(num) - 1
            if 0 <= idx < len(sources):
                sources[idx]['ai_analysis'] = {
                    'position': 'NEUTRE',
                    'confiance': 50,
                    'resume': f"Source neutre ou manque d'info"
                }
    
    return sources

