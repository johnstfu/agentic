"""
Tests for domain models
"""

import pytest
from datetime import datetime
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from domain.models import Source, VerdictData, VerificationStats, TraceEntry, VerificationResult


class TestSource:
    """Tests for Source dataclass"""
    
    def test_source_creation(self):
        """Test creating a source"""
        source = Source(
            url="https://example.com",
            title="Example Source",
            content="Some content here",
            tavily_score=0.85,
            trust_score=0.9,
            source_type="media",
            credibility_analysis="High credibility"
        )
        
        assert source.url == "https://example.com"
        assert source.trust_score == 0.9
        assert source.source_type == "media"
    
    def test_source_to_dict(self):
        """Test converting source to dict"""
        source = Source(
            url="https://example.com",
            title="Test",
            content="Content"
        )
        
        data = source.to_dict()
        assert isinstance(data, dict)
        assert data['url'] == "https://example.com"
        assert 'title' in data
    
    def test_source_from_dict(self):
        """Test creating source from dict"""
        data = {
            'url': 'https://test.com',
            'title': 'Test Title',
            'content': 'Test Content',
            'trust_score': 0.8
        }
        
        source = Source.from_dict(data)
        assert source.url == 'https://test.com'
        assert source.trust_score == 0.8
    
    def test_is_high_credibility(self):
        """Test high credibility check"""
        source_high = Source(url="test.com", title="Test", content="", trust_score=0.85)
        source_low = Source(url="test.com", title="Test", content="", trust_score=0.5)
        source_none = Source(url="test.com", title="Test", content="", trust_score=None)
        
        assert source_high.is_high_credibility() is True
        assert source_low.is_high_credibility() is False
        assert source_none.is_high_credibility() is False


class TestVerdictData:
    """Tests for VerdictData dataclass"""
    
    def test_verdict_creation(self):
        """Test creating a verdict"""
        verdict = VerdictData(
            verdict="VÉRIFIÉ",
            confidence=85,
            raw_analysis="This claim is verified"
        )
        
        assert verdict.verdict == "VÉRIFIÉ"
        assert verdict.confidence == 85
    
    def test_is_verified(self):
        """Test verified check"""
        verified = VerdictData(verdict="VÉRIFIÉ", confidence=90, raw_analysis="")
        partial = VerdictData(verdict="PARTIELLEMENT VÉRIFIÉ", confidence=60, raw_analysis="")
        false = VerdictData(verdict="NON VÉRIFIÉ", confidence=20, raw_analysis="")
        
        assert verified.is_verified() is True
        assert partial.is_verified() is False
        assert false.is_verified() is False
    
    def test_is_partially_verified(self):
        """Test partially verified check"""
        partial = VerdictData(verdict="PARTIELLEMENT VÉRIFIÉ", confidence=60, raw_analysis="")
        verified = VerdictData(verdict="VÉRIFIÉ", confidence=90, raw_analysis="")
        
        assert partial.is_partially_verified() is True
        assert verified.is_partially_verified() is False
    
    def test_is_false(self):
        """Test false check"""
        false = VerdictData(verdict="NON VÉRIFIÉ", confidence=20, raw_analysis="")
        verified = VerdictData(verdict="VÉRIFIÉ", confidence=90, raw_analysis="")
        
        assert false.is_false() is True
        assert verified.is_false() is False
    
    def test_verdict_to_dict(self):
        """Test converting verdict to dict"""
        verdict = VerdictData(
            verdict="VÉRIFIÉ",
            confidence=85,
            raw_analysis="Analysis"
        )
        
        data = verdict.to_dict()
        assert isinstance(data, dict)
        assert data['verdict'] == "VÉRIFIÉ"
        assert data['confidence'] == 85


class TestVerificationStats:
    """Tests for VerificationStats dataclass"""
    
    def test_stats_creation(self):
        """Test creating stats"""
        stats = VerificationStats(
            total_sources=10,
            high_credibility_sources=6,
            sources_confirment=5,
            sources_infirment=2,
            sources_neutres=3
        )
        
        assert stats.total_sources == 10
        assert stats.high_credibility_sources == 6
    
    def test_stats_to_dict(self):
        """Test converting stats to dict"""
        stats = VerificationStats(total_sources=5)
        data = stats.to_dict()
        
        assert isinstance(data, dict)
        assert data['total_sources'] == 5
    
    def test_stats_from_dict(self):
        """Test creating stats from dict"""
        data = {'total_sources': 8, 'high_credibility_sources': 4}
        stats = VerificationStats.from_dict(data)
        
        assert stats.total_sources == 8
        assert stats.high_credibility_sources == 4


class TestVerificationResult:
    """Tests for VerificationResult dataclass"""
    
    def test_result_creation(self):
        """Test creating a verification result"""
        verdict = VerdictData(verdict="VÉRIFIÉ", confidence=85, raw_analysis="Good")
        stats = VerificationStats(total_sources=5)
        
        result = VerificationResult(
            verdict=verdict,
            claim="Test claim",
            stats=stats,
            timestamp=datetime.now().isoformat()
        )
        
        assert result.claim == "Test claim"
        assert result.verdict.confidence == 85
    
    def test_is_successful(self):
        """Test successful verification check"""
        verdict_ok = VerdictData(verdict="VÉRIFIÉ", confidence=85, raw_analysis="")
        verdict_err = VerdictData(verdict="ERREUR", confidence=0, raw_analysis="")
        stats_ok = VerificationStats(total_sources=5)
        stats_empty = VerificationStats(total_sources=0)
        
        result_ok = VerificationResult(
            verdict=verdict_ok,
            claim="Test",
            stats=stats_ok,
            timestamp=""
        )
        
        result_err = VerificationResult(
            verdict=verdict_err,
            claim="Test",
            stats=stats_empty,
            timestamp=""
        )
        
        assert result_ok.is_successful() is True
        assert result_err.is_successful() is False
    
    def test_get_summary(self):
        """Test getting summary"""
        verdict = VerdictData(verdict="VÉRIFIÉ", confidence=85, raw_analysis="")
        stats = VerificationStats(total_sources=5)
        result = VerificationResult(
            verdict=verdict,
            claim="Test",
            stats=stats,
            timestamp=""
        )
        
        summary = result.get_summary()
        assert "VÉRIFIÉ" in summary
        assert "85" in summary
        assert "5" in summary
    
    def test_result_to_dict(self):
        """Test converting result to dict"""
        verdict = VerdictData(verdict="VÉRIFIÉ", confidence=85, raw_analysis="")
        stats = VerificationStats(total_sources=5)
        result = VerificationResult(
            verdict=verdict,
            claim="Test",
            stats=stats,
            timestamp="2024-11-03"
        )
        
        data = result.to_dict()
        assert isinstance(data, dict)
        assert 'verdict' in data
        assert 'stats' in data
        assert data['claim'] == "Test"

