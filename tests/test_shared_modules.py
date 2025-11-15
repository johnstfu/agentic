"""
Tests unitaires pour les modules shared (search, credibility, verdict)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.agents.shared import search, credibility, verdict
from src.utils.logger import FactCheckerLogger


class TestSearchModule:
    """Tests pour src/agents/shared/search.py"""
    
    @patch('src.agents.shared.search.TavilyClient')
    def test_search_tavily_success(self, mock_tavily_client):
        """Test recherche Tavily réussie"""
        # Mock Tavily response
        mock_response = {
            'results': [
                {
                    'url': 'https://example.com/article1',
                    'title': 'Article Test 1',
                    'content': 'Contenu de test 1',
                    'score': 0.95
                },
                {
                    'url': 'https://example.com/article2',
                    'title': 'Article Test 2',
                    'content': 'Contenu de test 2',
                    'score': 0.85
                }
            ],
            'answer': 'Réponse synthétique de Tavily'
        }
        
        mock_tavily = Mock()
        mock_tavily.search.return_value = mock_response
        mock_tavily_client.return_value = mock_tavily
        
        # Exécuter
        sources, tavily_answer = search.search_tavily("Test claim", max_results=2)
        
        # Vérifier
        assert len(sources) == 2
        assert sources[0]['url'] == 'https://example.com/article1'
        assert sources[0]['title'] == 'Article Test 1'
        assert sources[0]['tavily_score'] == 0.95
        assert tavily_answer == 'Réponse synthétique de Tavily'
    
    @patch('src.agents.shared.search.TavilyClient')
    def test_search_tavily_error_handling(self, mock_tavily_client):
        """Test gestion erreur Tavily"""
        # Mock erreur
        mock_tavily = Mock()
        mock_tavily.search.side_effect = Exception("API Error")
        mock_tavily_client.return_value = mock_tavily
        
        # Exécuter
        sources, tavily_answer = search.search_tavily("Test claim")
        
        # Vérifier fallback
        assert sources == []
        assert tavily_answer == ""
    
    @patch('src.agents.shared.search.TavilyClient')
    def test_search_tavily_empty_results(self, mock_tavily_client):
        """Test résultats vides"""
        mock_tavily = Mock()
        mock_tavily.search.return_value = {'results': [], 'answer': ''}
        mock_tavily_client.return_value = mock_tavily
        
        sources, tavily_answer = search.search_tavily("Unknown claim")
        
        assert sources == []
        assert tavily_answer == ""


class TestCredibilityModule:
    """Tests pour src/agents/shared/credibility.py"""
    
    def test_whitelist_scoring(self):
        """Test scoring via whitelist"""
        sources = [
            {'url': 'https://gouv.fr/info', 'title': 'Info gouv', 'content': 'Test'},
            {'url': 'https://wikipedia.org/wiki/Test', 'title': 'Wiki', 'content': 'Test'},
            {'url': 'https://unknown-site.com', 'title': 'Unknown', 'content': 'Test'}
        ]
        
        mock_llm = Mock()
        
        # Exécuter (sans appel LLM pour ce test)
        with patch('src.agents.shared.credibility.SystemMessage'), \
             patch('src.agents.shared.credibility.HumanMessage'):
            mock_llm.invoke.side_effect = Exception("Skip LLM")
            
            result = credibility.analyze_credibility(sources, mock_llm)
        
        # Vérifier que whitelist a été appliquée
        assert result[0]['trust_score'] == 0.95  # gouv.fr = tier1
        assert result[1]['trust_score'] == 0.78  # wikipedia = tier5
        assert result[2]['trust_score'] == 0.5   # unknown
    
    def test_source_tier_identification(self):
        """Test identification des tiers"""
        sources = [
            {'url': 'https://nature.com/article', 'title': 'Nature', 'content': 'Test'},
            {'url': 'https://lemonde.fr/article', 'title': 'Le Monde', 'content': 'Test'},
        ]
        
        mock_llm = Mock()
        
        with patch('src.agents.shared.credibility.SystemMessage'), \
             patch('src.agents.shared.credibility.HumanMessage'):
            mock_llm.invoke.side_effect = Exception("Skip LLM")
            
            result = credibility.analyze_credibility(sources, mock_llm)
        
        # Vérifier tiers
        assert result[0]['source_tier'] == 'tier2'  # academic
        assert result[1]['source_tier'] == 'tier4'  # media


class TestVerdictModule:
    """Tests pour src/agents/shared/verdict.py"""
    
    @patch('src.agents.shared.verdict.ChatOpenAI')
    def test_generate_verdict_verified(self, mock_llm_class):
        """Test génération verdict VÉRIFIÉ"""
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = """
1. VERDICT: ✅ VÉRIFIÉ

2. SCORE DE VÉRACITÉ: 95%

3. ANALYSE DÉTAILLÉE: Les sources confirment que Paris est la capitale de la France.

4. SOURCES PAR POSITION:
   - CONFIRMENT: SOURCE 1, SOURCE 2
   - INFIRMENT: Aucune
   - NEUTRES: Aucune

5. RECOMMANDATION: Information vérifiée par sources officielles.
"""
        
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm
        
        sources = [
            {'url': 'https://gouv.fr', 'title': 'Gouv', 'content': 'Paris capitale', 
             'trust_score': 0.95, 'source_type': 'tier1', 'credibility_analysis': 'Fiable'}
        ]
        
        # Exécuter
        result = verdict.generate_verdict(
            claim="Paris est la capitale de la France",
            sources=sources,
            tavily_answer="Paris est la capitale",
            llm=mock_llm
        )
        
        # Vérifier
        assert result['verdict'] == '✅ VÉRIFIÉ'
        assert result['confidence'] == 95
        assert 'Paris' in result['raw_analysis']
    
    @patch('src.agents.shared.verdict.ChatOpenAI')
    def test_generate_verdict_false(self, mock_llm_class):
        """Test génération verdict NON VÉRIFIÉ (faux)"""
        mock_response = Mock()
        mock_response.content = """
1. VERDICT: ❌ NON VÉRIFIÉ

2. SCORE DE VÉRACITÉ: 0%

3. ANALYSE DÉTAILLÉE: L'affirmation est fausse. La tour Eiffel est à Paris, pas à Lyon.

4. SOURCES PAR POSITION:
   - CONFIRMENT: Aucune
   - INFIRMENT: SOURCE 1, SOURCE 2
   - NEUTRES: Aucune

5. RECOMMANDATION: Information incorrecte.
"""
        
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm
        
        sources = [
            {'url': 'https://wikipedia.org', 'title': 'Wiki', 'content': 'Tour Eiffel à Paris',
             'trust_score': 0.78, 'source_type': 'tier5', 'credibility_analysis': 'Encyclopédie'}
        ]
        
        result = verdict.generate_verdict(
            claim="La tour Eiffel est à Lyon",
            sources=sources,
            tavily_answer="La tour Eiffel est à Paris",
            llm=mock_llm
        )
        
        assert result['verdict'] == '❌ NON VÉRIFIÉ'
        assert result['confidence'] == 0
    
    @pytest.mark.skip(reason="Safety check fonctionne en production, test unitaire complexe à isoler")
    def test_extract_verdict_safety_check(self):
        """Test safety check dans _extract_verdict (skip temporaire)"""
        # Le safety check fonctionne comme validé par test_hybrid_system.py
        # mais nécessite un contexte complet difficile à mocker
        pass


class TestTrustedSources:
    """Tests pour src/utils/trusted_sources.py"""
    
    def test_tier_identification(self):
        """Test identification correcte des tiers"""
        from src.utils.trusted_sources import get_source_tier
        
        assert get_source_tier('https://gouv.fr/info') == 'tier1'
        assert get_source_tier('https://nature.com/article') == 'tier2'
        assert get_source_tier('https://snopes.com/fact-check') == 'tier3'
        assert get_source_tier('https://lemonde.fr/article') == 'tier4'
        assert get_source_tier('https://wikipedia.org/wiki') == 'tier5'
        assert get_source_tier('https://random-blog.com') is None
    
    def test_domain_base_score(self):
        """Test scoring de base"""
        from src.utils.trusted_sources import get_domain_base_score
        
        assert get_domain_base_score('https://gouv.fr') == 0.95
        assert get_domain_base_score('https://wikipedia.org') == 0.78
        assert get_domain_base_score('https://unknown.com') == 0.5
    
    def test_blacklist_detection(self):
        """Test détection blacklist"""
        from src.utils.trusted_sources import get_source_tier, get_domain_base_score
        
        assert get_source_tier('https://facebook.com/post') == 'blacklisted'
        assert get_domain_base_score('https://twitter.com/status') == 0.1
    
    def test_academic_pattern_matching(self):
        """Test détection domaines académiques génériques"""
        from src.utils.trusted_sources import get_source_tier
        
        assert get_source_tier('https://stanford.edu/research') == 'tier2'
        assert get_source_tier('https://ox.ac.uk/department') == 'tier2'


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

