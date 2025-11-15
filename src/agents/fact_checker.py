"""
🔍 SMART FACT-CHECKER AMÉLIORÉ - Version 2.0
Tavily (Recherche Web) + OpenAI (Analyse Intelligente)
Avec caching, error handling, et rate limiting
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
import time

# OpenAI + LangChain
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# Tavily pour la recherche web
from tavily import TavilyClient

# Utilitaires
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import Config
from utils.logger import FactCheckerLogger
from utils.cache import SimpleCache

# Shared logic
from .shared import search, credibility, verdict


class SmartFactChecker:
    """
    Fact-Checker intelligent : Tavily (recherche) + OpenAI (analyse + évaluation crédibilité)

    Améliorations v2.0:
    - ✅ Caching des résultats (évite requêtes répétées)
    - ✅ Rate limiting (protection API)
    - ✅ Retry logic avec backoff exponentiel
    - ✅ Gestion d'erreurs robuste
    - ✅ Logging structuré
    """

    def __init__(self, enable_cache: bool = True):
        """Initialise le fact-checker avec Tavily + OpenAI"""

        # Validation config
        Config.validate()

        # Initialisation logger
        self.logger = FactCheckerLogger()

        # Initialisation cache
        self.cache = SimpleCache(ttl_seconds=Config.CACHE_TTL) if enable_cache else None

        # Rate limiting
        self.request_times: List[float] = []
        self.max_requests_per_minute = Config.MAX_REQUESTS_PER_MINUTE

        # Initialisation Tavily (recherche web avancée)
        try:
            self.tavily = TavilyClient(api_key=Config.TAVILY_API_KEY)
            self.logger.log("✅ Tavily initialisé")
        except Exception as e:
            self.logger.log(f"❌ Erreur Tavily: {str(e)}", "ERROR")
            raise

        # Initialisation OpenAI (analyse intelligente)
        try:
            self.llm = ChatOpenAI(
                model=Config.OPENAI_MODEL,
                temperature=Config.OPENAI_TEMPERATURE,
                openai_api_key=Config.OPENAI_API_KEY,
                request_timeout=60
            )
            self.logger.log("✅ OpenAI initialisé")
        except Exception as e:
            self.logger.log(f"❌ Erreur OpenAI: {str(e)}", "ERROR")
            raise

        self.logger.log(f"✅ {Config.APP_NAME} v{Config.APP_VERSION} prêt")

    def _check_rate_limit(self):
        """Vérifie et applique le rate limiting"""
        now = time.time()

        # Supprime les requêtes de plus d'1 minute
        self.request_times = [t for t in self.request_times if now - t < 60]

        # Si limite atteinte, attend
        if len(self.request_times) >= self.max_requests_per_minute:
            wait_time = 60 - (now - self.request_times[0])
            if wait_time > 0:
                self.logger.log(f"⏳ Rate limit atteint, attente de {wait_time:.1f}s", "WARNING")
                time.sleep(wait_time)

        self.request_times.append(now)

    def _retry_with_backoff(self, func, max_retries: int = 3, initial_delay: float = 1.0):
        """Execute une fonction avec retry et backoff exponentiel"""
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise

                delay = initial_delay * (2 ** attempt)
                self.logger.log(f"⚠️ Tentative {attempt + 1}/{max_retries} échouée, retry dans {delay}s", "WARNING")
                time.sleep(delay)

    def search_with_tavily(self, claim: str, max_results: int = 8) -> tuple:
        """
        Recherche avec Tavily (API de recherche web avancée)
        Avec retry logic et error handling
        """
        def _search():
            self._check_rate_limit()
            return search.search_tavily(claim, max_results, self.logger)
        
        try:
            return self._retry_with_backoff(_search)
        except Exception as e:
            self.logger.log(f"❌ Erreur Tavily retry: {str(e)}", "ERROR")
            return [], ""

    def analyze_sources_credibility(self, sources: List[Dict]) -> List[Dict]:
        """
        OpenAI analyse la crédibilité de chaque source dynamiquement
        Avec error handling robuste
        """
        def _analyze():
            self._check_rate_limit()
            return credibility.analyze_credibility(sources, self.llm, self.logger)
        
        try:
            return self._retry_with_backoff(_analyze)
        except Exception as e:
            self.logger.log(f"❌ Erreur credibility retry: {str(e)}", "ERROR")
            for source in sources:
                source['trust_score'] = 0.5
                source['source_type'] = 'unknown'
                source['credibility_analysis'] = 'Erreur analyse'
            return sources

    def analyze_claim_with_sources(self, claim: str, sources: List[Dict], tavily_answer: str) -> Dict:
        """
        OpenAI analyse l'affirmation avec les sources
        Avec error handling robuste
        """
        def _analyze():
            self._check_rate_limit()
            return verdict.generate_verdict(claim, sources, tavily_answer, self.llm, self.logger)
        
        try:
            return self._retry_with_backoff(_analyze)
        except Exception as e:
            self.logger.log(f"❌ Erreur verdict retry: {str(e)}", "ERROR")
            return {
                'verdict': 'ERREUR',
                'confidence': 0,
                'raw_analysis': f"Erreur: {str(e)}",
                'sources_analysis': []
            }


    def verify_claim(self, claim: str, context: str = "") -> Dict:
        """
        Méthode principale de vérification avec cache

        Returns:
            Dict avec verdict, score, analyse, sources, logs
        """
        # Check cache
        if self.cache:
            cached_result = self.cache.get(claim)
            if cached_result:
                self.logger.log("💾 Résultat trouvé dans le cache")
                cached_result['logs'] = self.logger.get_logs()
                cached_result['from_cache'] = True
                return cached_result

        self.logger.clear_logs()
        self.logger.log(f"🎯 Vérification: '{claim[:60]}...'")

        # 1. Recherche
        sources, tavily_answer = self.search_with_tavily(claim)

        if not sources:
            self.logger.log("⚠️ Aucune source trouvée")
            result = {
                'verdict': '❓ DONNÉES INSUFFISANTES',
                'confidence': 0,
                'raw_analysis': "Aucune source trouvée.",
                'sources': [],
                'logs': self.logger.get_logs(),
                'timestamp': datetime.now().isoformat(),
                'stats': {
                    'total_sources': 0,
                    'sources_confirment': 0,
                    'sources_infirment': 0,
                    'high_credibility_sources': 0
                },
                'from_cache': False
            }
            return result

        # 2. Analyse crédibilité
        sources = self.analyze_sources_credibility(sources)

        # 3. Analyse claim
        ai_result = self.analyze_claim_with_sources(claim, sources, tavily_answer)

        # 4. Statistiques
        stats = {
            'total_sources': len(sources),
            'sources_confirment': sum(1 for s in sources if s.get('ai_analysis', {}).get('position') == 'CONFIRME'),
            'sources_infirment': sum(1 for s in sources if s.get('ai_analysis', {}).get('position') == 'INFIRME'),
            'high_credibility_sources': sum(1 for s in sources if s.get('trust_score', 0) >= 0.7)
        }

        # 5. Résultat final
        result = {
            'verdict': ai_result['verdict'],
            'confidence': ai_result['confidence'],
            'raw_analysis': ai_result['raw_analysis'],
            'sources': sources,
            'logs': self.logger.get_logs(),
            'timestamp': datetime.now().isoformat(),
            'stats': stats,
            'source_name': f'{Config.APP_NAME} v{Config.APP_VERSION}',
            'from_cache': False
        }

        # Cache le résultat
        if self.cache:
            self.cache.set(claim, result)
            self.logger.log(f"💾 Résultat mis en cache (TTL: {Config.CACHE_TTL}s)")

        self.logger.log(f"✅ Vérification terminée")

        return result


# === TEST ===
if __name__ == "__main__":
    print("\n" + "="*60)
    print(f"🧪 TEST {Config.APP_NAME} v{Config.APP_VERSION}")
    print("="*60)

    checker = SmartFactChecker()

    test_claim = "La Tour Eiffel mesure 330 mètres de hauteur"

    print(f"\n🔍 Test: '{test_claim}'")
    result = checker.verify_claim(test_claim)

    print(f"\n📊 Résultat:")
    print(f"  Verdict: {result['verdict']}")
    print(f"  Confiance: {result['confidence']}%")
    print(f"  Sources: {result['stats']['total_sources']}")
    print(f"  Cache: {result.get('from_cache', False)}")
    print(f"\n✅ Test terminé!")
