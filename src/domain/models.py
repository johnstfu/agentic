"""
Domain models for fact-checking data structures
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class Source:
    """Represents a web source used for fact-checking"""
    
    url: str
    title: str
    content: str
    tavily_score: float = 0.0
    trust_score: Optional[float] = None
    source_type: Optional[str] = None
    credibility_analysis: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'url': self.url,
            'title': self.title,
            'content': self.content,
            'tavily_score': self.tavily_score,
            'trust_score': self.trust_score,
            'source_type': self.source_type,
            'credibility_analysis': self.credibility_analysis
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Source':
        """Create from dictionary"""
        return cls(
            url=data.get('url', ''),
            title=data.get('title', 'Sans titre'),
            content=data.get('content', ''),
            tavily_score=data.get('tavily_score', 0.0),
            trust_score=data.get('trust_score'),
            source_type=data.get('source_type'),
            credibility_analysis=data.get('credibility_analysis')
        )
    
    def is_high_credibility(self, threshold: float = 0.7) -> bool:
        """Check if source has high credibility"""
        return self.trust_score is not None and self.trust_score >= threshold


@dataclass
class VerdictData:
    """Represents a fact-checking verdict"""
    
    verdict: str
    confidence: int
    raw_analysis: str
    sources: List[Source] = field(default_factory=list)
    sources_analysis: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'verdict': self.verdict,
            'confidence': self.confidence,
            'raw_analysis': self.raw_analysis,
            'sources': [s.to_dict() for s in self.sources],
            'sources_analysis': self.sources_analysis
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VerdictData':
        """Create from dictionary"""
        sources = [Source.from_dict(s) for s in data.get('sources', [])]
        return cls(
            verdict=data.get('verdict', 'INCONNU'),
            confidence=data.get('confidence', 50),
            raw_analysis=data.get('raw_analysis', ''),
            sources=sources,
            sources_analysis=data.get('sources_analysis', [])
        )
    
    def is_verified(self) -> bool:
        """Check if claim is verified"""
        return "VÉRIFIÉ" in self.verdict and "NON" not in self.verdict and "PARTIELLEMENT" not in self.verdict
    
    def is_partially_verified(self) -> bool:
        """Check if claim is partially verified"""
        return "PARTIELLEMENT" in self.verdict
    
    def is_false(self) -> bool:
        """Check if claim is false"""
        return "NON VÉRIFIÉ" in self.verdict


@dataclass
class VerificationStats:
    """Statistics about a verification process"""
    
    total_sources: int = 0
    high_credibility_sources: int = 0
    sources_confirment: int = 0
    sources_infirment: int = 0
    sources_neutres: int = 0
    verification_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'total_sources': self.total_sources,
            'high_credibility_sources': self.high_credibility_sources,
            'sources_confirment': self.sources_confirment,
            'sources_infirment': self.sources_infirment,
            'sources_neutres': self.sources_neutres,
            'verification_time': self.verification_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VerificationStats':
        """Create from dictionary"""
        return cls(
            total_sources=data.get('total_sources', 0),
            high_credibility_sources=data.get('high_credibility_sources', 0),
            sources_confirment=data.get('sources_confirment', 0),
            sources_infirment=data.get('sources_infirment', 0),
            sources_neutres=data.get('sources_neutres', 0),
            verification_time=data.get('verification_time')
        )


@dataclass
class TraceEntry:
    """Represents one step in the verification trace"""
    
    step: str
    timestamp: str
    reasoning: Optional[str] = None
    sources_found: Optional[int] = None
    high_credibility_count: Optional[int] = None
    decision: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'step': self.step,
            'timestamp': self.timestamp,
            'reasoning': self.reasoning,
            'sources_found': self.sources_found,
            'high_credibility_count': self.high_credibility_count,
            'decision': self.decision,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TraceEntry':
        """Create from dictionary"""
        return cls(
            step=data.get('step', ''),
            timestamp=data.get('timestamp', ''),
            reasoning=data.get('reasoning'),
            sources_found=data.get('sources_found'),
            high_credibility_count=data.get('high_credibility_count'),
            decision=data.get('decision'),
            metadata=data.get('metadata', {})
        )


@dataclass
class VerificationResult:
    """Complete fact-checking result"""
    
    verdict: VerdictData
    claim: str
    stats: VerificationStats
    timestamp: str
    source_name: str = "VérificateurIA"
    from_cache: bool = False
    trace: List[TraceEntry] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'verdict': self.verdict.to_dict(),
            'claim': self.claim,
            'stats': self.stats.to_dict(),
            'timestamp': self.timestamp,
            'source_name': self.source_name,
            'from_cache': self.from_cache,
            'trace': [t.to_dict() for t in self.trace],
            'logs': self.logs
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VerificationResult':
        """Create from dictionary"""
        verdict = VerdictData.from_dict(data.get('verdict', {}))
        stats = VerificationStats.from_dict(data.get('stats', {}))
        trace = [TraceEntry.from_dict(t) for t in data.get('trace', [])]
        
        return cls(
            verdict=verdict,
            claim=data.get('claim', ''),
            stats=stats,
            timestamp=data.get('timestamp', datetime.now().isoformat()),
            source_name=data.get('source_name', 'VérificateurIA'),
            from_cache=data.get('from_cache', False),
            trace=trace,
            logs=data.get('logs', [])
        )
    
    def is_successful(self) -> bool:
        """Check if verification was successful"""
        return self.verdict.verdict != 'ERREUR' and self.stats.total_sources > 0
    
    def get_summary(self) -> str:
        """Get a short summary of the result"""
        return f"{self.verdict.verdict} ({self.verdict.confidence}%) - {self.stats.total_sources} sources"

