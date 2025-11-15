"""
Tests unitaires pour l'agent de fact-checking
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.fact_checker import SmartFactChecker
from utils.config import Config


def test_agent_initialization():
    """Test d'initialisation de l'agent"""
    try:
        agent = SmartFactChecker(enable_cache=False)
        assert agent is not None
        assert agent.tavily is not None
        assert agent.llm is not None
    except ValueError:
        # Clés API manquantes (normal en environnement de test)
        pytest.skip("Clés API manquantes")


def test_cache_system():
    """Test du système de cache"""
    from utils.cache import SimpleCache

    cache = SimpleCache(ttl_seconds=60)

    # Test set/get
    test_claim = "Test claim"
    test_data = {"verdict": "TEST", "confidence": 100}

    cache.set(test_claim, test_data)
    retrieved = cache.get(test_claim)

    assert retrieved is not None
    assert retrieved['verdict'] == "TEST"
    assert retrieved['confidence'] == 100

    # Test clear
    cache.clear()
    assert cache.size() == 0


@pytest.mark.skip(reason="Méthodes migrées vers src/agents/shared/verdict.py - voir test_shared_modules.py")
def test_score_extraction():
    """Test de l'extraction du score (obsolète - migré)"""
    pass


@pytest.mark.skip(reason="Méthodes migrées vers src/agents/shared/verdict.py - voir test_shared_modules.py")
def test_verdict_extraction():
    """Test de l'extraction du verdict (obsolète - migré)"""
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
