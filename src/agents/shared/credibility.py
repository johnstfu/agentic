"""
Source credibility analysis logic - extracted from fact_checker.py
"""

import json
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.logger import FactCheckerLogger
from utils.trusted_sources import (
    get_domain_base_score, 
    get_source_tier, 
    get_tier_description,
    calculate_trust_score
)


def analyze_credibility(sources: List[Dict], llm: ChatOpenAI, logger: FactCheckerLogger = None) -> List[Dict]:
    """
    Analyze credibility of sources using OpenAI
    
    Args:
        sources: List of source dictionaries
        llm: ChatOpenAI instance
        logger: Optional logger instance
        
    Returns:
        Sources list with added credibility scores
    """
    if logger is None:
        logger = FactCheckerLogger()
    
    logger.log("🤖 Analyse crédibilité des sources...")
    
    if not sources:
        return sources
    
    # ÉTAPE 1: Scoring de base via whitelist
    for idx, source in enumerate(sources):
        url = source['url']
        base_score = get_domain_base_score(url)
        tier = get_source_tier(url)
        
        source['trust_score'] = base_score
        source['source_tier'] = tier if tier else 'unknown'
        source['tier_description'] = get_tier_description(tier) if tier else "Source non classée"
        
        # Log pour debug
        if tier and tier != 'unknown':
            logger.log(f"📊 Source {idx+1}: {tier} (score={base_score:.2f}) - {url[:50]}...")
    
    # ÉTAPE 2: Préparer contexte pour analyse LLM (optionnelle/enrichissement)
    sources_context = ""
    for idx, source in enumerate(sources, 1):
        sources_context += f"""
SOURCE {idx}:
- URL: {source['url']}
- Titre: {source['title']}
- Contenu: {source['content'][:400]}...
- Score Whitelist: {source['trust_score']:.2f} ({source.get('source_tier', 'unknown')})
---
"""
    
    system_prompt = """Tu es un expert en évaluation de crédibilité des sources web.

SCORING STRICT (0.0 à 1.0):
- 0.95-1.0: Gouvernements nationaux (.gov, .gouv), OMS, ONU, institutions UE officielles
- 0.85-0.94: Universités prestigieuses (.edu, .ac), Nature, Science, Lancet
- 0.75-0.84: Médias établis haute réputation (Reuters, BBC, AFP, AP, Le Monde)
- 0.60-0.74: Médias généralistes reconnus
- 0.40-0.59: Blogs d'experts, médias locaux, sites spécialisés
- 0.20-0.39: Sources peu connues
- 0.00-0.19: Sources douteuses

FORMAT JSON STRICT:
{
  "sources": [
    {
      "source_index": 1,
      "source_type": "government|academic|media|blog|unknown",
      "credibility_score": 0.85,
      "credibility_analysis": "Justification du score"
    }
  ]
}"""
    
    user_prompt = f"""Analyse la crédibilité de ces sources:

{sources_context}

Réponds UNIQUEMENT en JSON valide."""
    
    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = llm.invoke(messages)
        analysis = response.content
        
        # Parse JSON
        try:
            json_start = analysis.find('{')
            json_end = analysis.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = analysis[json_start:json_end]
                credibility_data = json.loads(json_str)
                
                for source_data in credibility_data.get('sources', []):
                    idx = source_data['source_index'] - 1
                    if 0 <= idx < len(sources):
                        sources[idx]['trust_score'] = source_data['credibility_score']
                        sources[idx]['source_type'] = source_data['source_type']
                        sources[idx]['credibility_analysis'] = source_data['credibility_analysis']
                
                logger.log(f"✅ Crédibilité analysée pour {len(sources)} sources")
            else:
                raise ValueError("JSON non trouvé")
        
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.log(f"⚠️ Erreur parsing JSON, utilisation whitelist uniquement", "WARNING")
            # Fallback: on garde les scores whitelist déjà assignés en étape 1
            for source in sources:
                # trust_score déjà assigné via whitelist
                tier = source.get('source_tier', 'unknown')
                source['source_type'] = tier
                source['credibility_analysis'] = f"Score whitelist: {tier} ({source['trust_score']:.2f})"
        
        return sources
    
    except Exception as e:
        logger.log(f"❌ Erreur analyse crédibilité: {str(e)}", "ERROR")
        # Fallback minimal: garder les scores whitelist si déjà assignés
        for source in sources:
            if 'trust_score' not in source:
                # Si pas encore de score, utiliser whitelist
                source['trust_score'] = get_domain_base_score(source['url'])
                source['source_type'] = get_source_tier(source['url']) or 'unknown'
            source['credibility_analysis'] = 'Erreur analyse LLM - score whitelist utilisé'
        return sources

