"""
Unit tests for FactCheckerGraph (v3.0)
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.fact_checker_graph import FactCheckerGraph, FactCheckState


def test_graph_initialization():
    """Test that graph initializes correctly"""
    graph = FactCheckerGraph(enable_hitl=False)
    
    assert graph is not None
    assert graph.graph is not None
    assert graph.llm is not None
    assert graph.persistence is not None


def test_basic_flow_without_hitl():
    """Test basic workflow without interruptions"""
    graph = FactCheckerGraph(enable_hitl=False, enable_cache=False)
    
    # Simple test claim
    result = graph.verify("Python is a programming language", user_id="test")
    
    assert 'verdict' in result
    assert 'sources' in result
    assert 'trace' in result
    assert 'stats' in result
    
    # Check verdict structure
    verdict = result['verdict']
    assert 'verdict' in verdict
    assert 'confidence' in verdict
    assert 'raw_analysis' in verdict
    
    # Check confidence is in valid range
    assert 0 <= verdict['confidence'] <= 100


def test_persistence_manager():
    """Test persistence functionality"""
    from utils.persistence import PersistenceManager
    
    persistence = PersistenceManager("test_fact_checks.db")
    
    # Should not crash
    history = persistence.get_user_history("test_user", limit=5)
    assert isinstance(history, list)
    
    # Clean up
    import os
    if os.path.exists("test_fact_checks.db"):
        os.remove("test_fact_checks.db")


def test_decide_search_strategy():
    """Test multi-step reasoning decision logic"""
    graph = FactCheckerGraph(enable_hitl=False)
    
    # Test case 1: Few sources -> deep search
    state_few_sources = FactCheckState(
        claim="Test claim",
        sources=[{'url': 'test.com'}],  # Only 1 source
        trace=[]
    )
    
    decision = graph._decide_search_strategy(state_few_sources)
    assert decision == 'deep_search'
    
    # Test case 2: Many high-quality sources -> fast verdict
    state_high_quality = FactCheckState(
        claim="Test claim",
        sources=[
            {'url': f'test{i}.com', 'trust_score': 0.9} 
            for i in range(5)
        ],
        credibility_analyzed=True,
        trace=[]
    )
    
    decision = graph._decide_search_strategy(state_high_quality)
    assert decision == 'fast_verdict'
    
    # Test case 3: Normal case -> standard
    state_normal = FactCheckState(
        claim="Test claim",
        sources=[
            {'url': f'test{i}.com', 'trust_score': 0.6} 
            for i in range(5)
        ],
        trace=[]
    )
    
    decision = graph._decide_search_strategy(state_normal)
    assert decision == 'standard'


def test_batch_verification():
    """Test batch processing"""
    graph = FactCheckerGraph(enable_hitl=False, enable_cache=False)
    
    claims = [
        "Python is a programming language",
        "The Earth is flat"
    ]
    
    # Note: This will make real API calls
    # In production, you'd mock the API calls
    result = graph.verify_batch(claims, user_id="test_batch")
    
    assert 'results' in result
    assert 'comparison' in result
    assert 'stats' in result
    
    assert len(result['results']) == len(claims)
    assert result['stats']['total'] == len(claims)


def test_feedback_manager():
    """Test feedback collection"""
    from utils.feedback import FeedbackManager
    
    feedback_mgr = FeedbackManager("test_feedback.db")
    
    # Collect some feedback
    feedback_mgr.collect_feedback(
        claim="Test claim",
        verdict={'verdict': '✅ VÉRIFIÉ', 'confidence': 85},
        user_feedback={
            'rating': 5,
            'comment': 'Great!',
            'correct_verdict': None
        }
    )
    
    # Get stats
    stats = feedback_mgr.get_stats()
    assert stats['total_feedback'] >= 1
    assert 0 <= stats['average_rating'] <= 5
    
    # Clean up
    import os
    if os.path.exists("test_feedback.db"):
        os.remove("test_feedback.db")


def test_explainability():
    """Test decision trace and explanation"""
    from utils.explainability import DecisionTrace
    
    trace = [
        {
            'step': 'search',
            'timestamp': '2024-01-01T00:00:00',
            'sources_found': 8,
            'reasoning': 'Searched for claim'
        },
        {
            'step': 'credibility',
            'timestamp': '2024-01-01T00:00:01',
            'high_credibility_count': 5,
            'reasoning': 'Analyzed credibility'
        }
    ]
    
    # Generate decision tree
    tree = DecisionTrace.generate_decision_tree(trace)
    assert tree['root'] == 'search'
    assert len(tree['nodes']) == 2
    assert tree['total_steps'] == 2
    
    # Generate explanation
    verdict = {'verdict': '✅ VÉRIFIÉ', 'confidence': 85}
    sources = [
        {
            'title': 'Test Source',
            'url': 'https://test.com',
            'trust_score': 0.9
        }
    ]
    
    explanation = DecisionTrace.explain_verdict(verdict, sources, trace)
    assert '✅ VÉRIFIÉ' in explanation
    assert 'Test Source' in explanation


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

