"""
Tavily search logic - extracted from fact_checker.py for reusability
"""

import time
from typing import Tuple, List, Dict
from tavily import TavilyClient
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.config import Config
from utils.logger import FactCheckerLogger


def search_tavily(claim: str, max_results: int = 8, logger: FactCheckerLogger = None) -> Tuple[List[Dict], str]:
    """
    Search with Tavily API
    
    Args:
        claim: The claim to search for
        max_results: Maximum number of results to return
        logger: Optional logger instance
        
    Returns:
        Tuple of (sources list, tavily answer string)
    """
    if logger is None:
        logger = FactCheckerLogger()
    
    logger.log(f"🔍 Recherche Tavily: '{claim[:50]}...'")
    
    try:
        tavily = TavilyClient(api_key=Config.TAVILY_API_KEY)
        
        response = tavily.search(
            query=claim,
            max_results=max_results,
            search_depth=Config.TAVILY_SEARCH_DEPTH,
            include_answer=True,
            include_raw_content=False,
            include_images=False
        )
        
        sources = []
        for result in response.get('results', []):
            sources.append({
                'url': result.get('url', ''),
                'title': result.get('title', 'Sans titre'),
                'content': result.get('content', ''),
                'tavily_score': result.get('score', 0),
                'trust_score': None,
                'source_type': None,
                'credibility_analysis': None
            })
        
        tavily_answer = response.get('answer', '')
        logger.log(f"✅ Tavily: {len(sources)} sources trouvées")
        
        return sources, tavily_answer
        
    except Exception as e:
        logger.log(f"❌ Erreur Tavily: {str(e)}", "ERROR")
        return [], ""

