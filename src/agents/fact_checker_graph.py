"""
LangGraph-based fact-checker with Human-in-the-Loop capabilities (v3.0)
"""

from typing import TypedDict, List, Dict, Optional
from datetime import datetime
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langchain_openai import ChatOpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import Config
from utils.logger import FactCheckerLogger
from utils.persistence import PersistenceManager
from .shared import search, credibility, verdict


class FactCheckState(TypedDict, total=False):
    """State for fact-checking workflow"""
    # Input
    claim: str
    user_id: str
    context: str
    
    # Workflow data
    sources: List[Dict]
    tavily_answer: str
    credibility_analyzed: bool
    
    # Results
    verdict: Dict
    confidence: int
    analysis: str
    
    # Metadata
    step: str
    needs_deep_search: bool
    human_validated: bool
    feedback: Optional[Dict]
    trace: List[Dict]
    timestamp: str


class FactCheckerGraph:
    """LangGraph-based fact-checker with HITL"""
    
    def __init__(self, enable_hitl: bool = True, enable_cache: bool = True):
        """
        Initialize fact-checker graph
        
        Args:
            enable_hitl: Enable Human-in-the-Loop interrupts
            enable_cache: Enable caching
        """
        self.enable_hitl = enable_hitl
        self.enable_cache = enable_cache
        
        # Initialize components
        self.logger = FactCheckerLogger()
        self.llm = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            temperature=Config.OPENAI_TEMPERATURE,
            openai_api_key=Config.OPENAI_API_KEY,
            request_timeout=60
        )
        
        # Persistence - Use PersistenceManager properly
        self.persistence = PersistenceManager(Config.PERSISTENCE_DB)
        self.checkpointer = self.persistence.checkpointer
        
        # Build graph
        self.graph = self._build_graph()
        
        self.logger.log(f"✅ FactCheckerGraph v3.0 initialized (HITL: {enable_hitl})")
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(FactCheckState)
        
        # Add nodes
        workflow.add_node("search", self._search_node)
        workflow.add_node("source_validation", self._source_validation_node)
        workflow.add_node("credibility", self._credibility_node)
        workflow.add_node("verdict", self._verdict_node)
        workflow.add_node("verdict_validation", self._verdict_validation_node)
        workflow.add_node("deep_search", self._deep_search_node)
        workflow.add_node("neutral_search", self._neutral_search_node)
        
        # Set entry point
        workflow.set_entry_point("search")
        
        # Add edges
        if self.enable_hitl:
            workflow.add_edge("search", "source_validation")
            workflow.add_conditional_edges(
                "source_validation",
                self._decide_search_strategy,
                {
                    'deep_search': 'deep_search',
                    'neutral_search': 'neutral_search',
                    'fast_verdict': 'verdict',
                    'standard': 'credibility'
                }
            )
            workflow.add_edge("deep_search", "credibility")
            workflow.add_edge("neutral_search", "credibility")
            workflow.add_edge("credibility", "verdict")
            workflow.add_edge("verdict", "verdict_validation")
            workflow.add_edge("verdict_validation", END)
        else:
            # Simple flow without HITL
            workflow.add_edge("search", "credibility")
            workflow.add_edge("credibility", "verdict")
            workflow.add_edge("verdict", END)
        
        # Compile with persistence (keep connection alive)
        compiled = workflow.compile(checkpointer=self.checkpointer)
        
        return compiled
    
    # ===== NODES =====
    
    def _search_node(self, state: FactCheckState) -> Dict:
        """Search for sources using Tavily"""
        claim = state['claim']
        max_results = 12 if state.get('needs_deep_search') else 8
        
        sources, answer = search.search_tavily(claim, max_results, self.logger)
        
        trace_entry = {
            'step': 'search',
            'timestamp': datetime.now().isoformat(),
            'sources_found': len(sources),
            'reasoning': f'Recherché "{claim}" avec Tavily'
        }
        
        return {
            'sources': sources,
            'tavily_answer': answer,
            'step': 'search_completed',
            'trace': state.get('trace', []) + [trace_entry],
            'timestamp': datetime.now().isoformat()
        }
    
    def _source_validation_node(self, state: FactCheckState) -> Dict:
        """HITL: Human validation of sources"""
        if not self.enable_hitl:
            return {'human_validated': True}
        
        sources = state['sources']
        
        validated = interrupt({
            'type': 'source_validation',
            'claim': state['claim'],
            'sources_preview': [
                {
                    'index': i,
                    'url': s['url'],
                    'title': s['title'],
                    'snippet': s['content'][:200],
                    'tavily_score': s.get('tavily_score', 0)
                }
                for i, s in enumerate(sources)
            ],
            'question': 'Valider les sources pour analyse ?',
            'options': ['approve_all', 'select', 'reject_and_reformulate']
        })
        
        if validated['action'] == 'select':
            sources = [sources[i] for i in validated['selected_indices']]
        elif validated['action'] == 'reject_and_reformulate':
            return Command(
                update={'claim': validated['reformulated_query'], 'trace': state.get('trace', []) + [{
                    'step': 'source_validation',
                    'action': 'reformulated',
                    'new_query': validated['reformulated_query']
                }]},
                goto='search'
            )
        
        trace_entry = {
            'step': 'source_validation',
            'timestamp': datetime.now().isoformat(),
            'action': validated['action'],
            'kept_sources': len(sources),
            'reasoning': f"Humain a validé {len(sources)} sources"
        }
        
        return {
            'sources': sources,
            'human_validated': True,
            'trace': state.get('trace', []) + [trace_entry]
        }
    
    def _credibility_node(self, state: FactCheckState) -> Dict:
        """Analyze source credibility"""
        sources = state['sources']
        analyzed_sources = credibility.analyze_credibility(sources, self.llm, self.logger)
        
        high_cred_count = sum(1 for s in analyzed_sources if s.get('trust_score', 0) >= 0.7)
        
        trace_entry = {
            'step': 'credibility',
            'timestamp': datetime.now().isoformat(),
            'high_credibility_count': high_cred_count,
            'reasoning': f'Analysé crédibilité de {len(analyzed_sources)} sources'
        }
        
        return {
            'sources': analyzed_sources,
            'credibility_analyzed': True,
            'trace': state.get('trace', []) + [trace_entry]
        }
    
    def _verdict_node(self, state: FactCheckState) -> Dict:
        """Generate verdict"""
        claim = state['claim']
        sources = state['sources']
        tavily_answer = state.get('tavily_answer', '')
        
        verdict_result = verdict.generate_verdict(claim, sources, tavily_answer, self.llm, self.logger)
        
        trace_entry = {
            'step': 'verdict',
            'timestamp': datetime.now().isoformat(),
            'verdict_generated': verdict_result['verdict'],
            'confidence': verdict_result['confidence'],
            'reasoning': f"Généré verdict: {verdict_result['verdict']} ({verdict_result['confidence']}%)"
        }
        
        return {
            'verdict': verdict_result,
            'confidence': verdict_result['confidence'],
            'analysis': verdict_result['raw_analysis'],
            'trace': state.get('trace', []) + [trace_entry]
        }
    
    def _verdict_validation_node(self, state: FactCheckState) -> Dict:
        """HITL: Human validation of verdict before publication"""
        if not self.enable_hitl:
            return {}
        
        verdict_data = state['verdict']
        
        final = interrupt({
            'type': 'verdict_review',
            'claim': state['claim'],
            'verdict': verdict_data['verdict'],
            'confidence': verdict_data['confidence'],
            'analysis': verdict_data['raw_analysis'],
            'sources': state['sources'],
            'question': 'Approuver ce verdict pour publication ?',
            'options': ['approve', 'edit', 'reject']
        })
        
        if final['action'] == 'edit':
            verdict_data.update({
                'verdict': final.get('edited_verdict', verdict_data['verdict']),
                'confidence': final.get('edited_confidence', verdict_data['confidence']),
                'raw_analysis': verdict_data['raw_analysis'] + f"\n\n[Note éditeur: {final.get('editor_note', '')}]",
                'human_edited': True
            })
            
            trace_entry = {
                'step': 'verdict_validation',
                'timestamp': datetime.now().isoformat(),
                'action': 'edited',
                'reasoning': f"Verdict modifié par humain: {final.get('editor_note', '')}"
            }
        elif final['action'] == 'reject':
            return Command(
                update={'trace': state.get('trace', []) + [{
                    'step': 'verdict_validation',
                    'action': 'rejected',
                    'reasoning': 'Humain a rejeté le verdict, recommence'
                }]},
                goto='search'
            )
        else:  # approve
            trace_entry = {
                'step': 'verdict_validation',
                'timestamp': datetime.now().isoformat(),
                'action': 'approved',
                'reasoning': 'Verdict approuvé par humain'
            }
        
        return {
            'verdict': verdict_data,
            'trace': state.get('trace', []) + [trace_entry]
        }
    
    def _deep_search_node(self, state: FactCheckState) -> Dict:
        """Deep search if insufficient sources"""
        claim = state['claim']
        sources, answer = search.search_tavily(claim, max_results=15, logger=self.logger)
        
        trace_entry = {
            'step': 'deep_search',
            'timestamp': datetime.now().isoformat(),
            'sources_found': len(sources),
            'reasoning': 'Recherche approfondie car sources insuffisantes'
        }
        
        return {
            'sources': sources,
            'tavily_answer': answer,
            'trace': state.get('trace', []) + [trace_entry]
        }
    
    def _neutral_search_node(self, state: FactCheckState) -> Dict:
        """Neutral search if contradictory sources"""
        claim = state['claim']
        neutral_query = f"scientific facts about {claim}"
        sources, answer = search.search_tavily(neutral_query, max_results=10, logger=self.logger)
        
        # Add to existing sources
        all_sources = state['sources'] + sources
        
        trace_entry = {
            'step': 'neutral_search',
            'timestamp': datetime.now().isoformat(),
            'sources_added': len(sources),
            'reasoning': 'Recherche neutre car sources contradictoires'
        }
        
        return {
            'sources': all_sources,
            'trace': state.get('trace', []) + [trace_entry]
        }
    
    def _decide_search_strategy(self, state: FactCheckState) -> str:
        """Decide next search strategy based on context"""
        sources = state.get('sources', [])
        
        # If too few sources
        if len(sources) < 3:
            return 'deep_search'
        
        # If sources contradictory (after credibility)
        if state.get('credibility_analyzed'):
            positions = [s.get('position') for s in sources if s.get('position')]
            if 'CONFIRME' in positions and 'INFIRME' in positions:
                return 'neutral_search'
        
        # If high average credibility
        avg_cred = sum(s.get('trust_score', 0.5) for s in sources) / len(sources) if sources else 0
        if avg_cred >= 0.8:
            return 'fast_verdict'
        
        return 'standard'
    
    # ===== PUBLIC METHODS =====
    
    def verify(self, claim: str, user_id: str = "default", context: str = "") -> Dict:
        """
        Verify a claim (simple, without persistence tracking)
        
        Args:
            claim: Claim to verify
            user_id: User identifier
            context: Additional context
            
        Returns:
            Verification result dict
        """
        config = {"configurable": {"thread_id": f"{user_id}_{datetime.now().timestamp()}"}}
        
        initial_state = {
            'claim': claim,
            'user_id': user_id,
            'context': context,
            'trace': [],
            'timestamp': datetime.now().isoformat()
        }
        
        result = self.graph.invoke(initial_state, config)
        
        return self._format_result(result)
    
    def verify_with_persistence(self, claim: str, user_id: str = "default") -> Dict:
        """
        Verify claim with persistence and history check
        
        Args:
            claim: Claim to verify
            user_id: User identifier
            
        Returns:
            Verification result dict
        """
        # Check for similar claims
        similar = self.persistence.find_similar_claims(claim, user_id)
        if similar:
            self.logger.log(f"💾 Claim similaire trouvée dans l'historique")
            # Could return similar or continue with new verification
        
        config = {"configurable": {"thread_id": f"{user_id}_{datetime.now().timestamp()}"}}
        
        initial_state = {
            'claim': claim,
            'user_id': user_id,
            'trace': [],
            'timestamp': datetime.now().isoformat()
        }
        
        result = self.graph.invoke(initial_state, config)
        
        return self._format_result(result)
    
    def verify_batch(self, claims: List[str], user_id: str = "batch") -> Dict:
        """
        Verify multiple claims in parallel
        
        Args:
            claims: List of claims to verify
            user_id: User identifier
            
        Returns:
            Batch results with comparison
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self.verify_with_persistence, claim, f"{user_id}_{i}"): (i, claim)
                for i, claim in enumerate(claims)
            }
            
            for future in as_completed(futures):
                idx, claim = futures[future]
                try:
                    result = future.result()
                    results.append({'index': idx, 'claim': claim, 'result': result})
                except Exception as e:
                    results.append({'index': idx, 'claim': claim, 'error': str(e)})
        
        # Sort by original index
        results.sort(key=lambda x: x['index'])
        
        # Comparative analysis
        comparison = self._compare_results(results)
        
        return {
            'results': results,
            'comparison': comparison,
            'stats': {
                'total': len(claims),
                'verified': sum(1 for r in results if '✅' in r.get('result', {}).get('verdict', {}).get('verdict', '')),
                'rejected': sum(1 for r in results if '❌' in r.get('result', {}).get('verdict', {}).get('verdict', '')),
                'uncertain': sum(1 for r in results if '⚠️' in r.get('result', {}).get('verdict', {}).get('verdict', ''))
            }
        }
    
    def _compare_results(self, results: List[Dict]) -> Dict:
        """Compare batch results"""
        confidences = [
            r.get('result', {}).get('verdict', {}).get('confidence', 0) 
            for r in results if 'result' in r
        ]
        
        if not confidences:
            return {
                'avg_confidence': 0,
                'min_confidence': 0,
                'max_confidence': 0
            }
        
        return {
            'avg_confidence': sum(confidences) / len(confidences),
            'min_confidence': min(confidences),
            'max_confidence': max(confidences),
            'most_credible': max(
                results, 
                key=lambda r: r.get('result', {}).get('verdict', {}).get('confidence', 0)
            ),
            'least_credible': min(
                results,
                key=lambda r: r.get('result', {}).get('verdict', {}).get('confidence', 100)
            )
        }
    
    def _format_result(self, state: Dict) -> Dict:
        """Format final result"""
        verdict_data = state.get('verdict', {})
        sources = state.get('sources', [])
        trace = state.get('trace', [])
        
        # Calculate stats
        stats = {
            'total_sources': len(sources),
            'sources_confirment': sum(1 for s in sources if s.get('ai_analysis', {}).get('position') == 'CONFIRME'),
            'sources_infirment': sum(1 for s in sources if s.get('ai_analysis', {}).get('position') == 'INFIRME'),
            'high_credibility_sources': sum(1 for s in sources if s.get('trust_score', 0) >= 0.7)
        }
        
        return {
            'verdict': verdict_data,
            'sources': sources,
            'trace': trace,
            'stats': stats,
            'timestamp': state.get('timestamp', datetime.now().isoformat()),
            'source_name': f'{Config.APP_NAME} v3.0',
            'from_cache': False
        }
    
    def close(self):
        """Close persistence manager and cleanup resources"""
        if hasattr(self, 'persistence'):
            self.persistence.close()
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close()


# === TEST ===
if __name__ == "__main__":
    print("\n" + "="*60)
    print(f"🧪 TEST FactCheckerGraph v3.0")
    print("="*60)
    
    graph = FactCheckerGraph(enable_hitl=False)
    
    test_claim = "La Tour Eiffel mesure 330 mètres de hauteur"
    
    print(f"\n🔍 Test: '{test_claim}'")
    result = graph.verify(test_claim, user_id="test")
    
    print(f"\n📊 Résultat:")
    print(f"  Verdict: {result['verdict']['verdict']}")
    print(f"  Confiance: {result['verdict']['confidence']}%")
    print(f"  Sources: {result['stats']['total_sources']}")
    print(f"\n✅ Test terminé!")

