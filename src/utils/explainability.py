"""
Explainability and decision tracing system
"""

from typing import List, Dict
import json


class DecisionTrace:
    """Trace and explain agent decisions"""
    
    @staticmethod
    def generate_decision_tree(trace: List[Dict]) -> Dict:
        """
        Build decision tree from trace
        
        Args:
            trace: List of trace entries
            
        Returns:
            Decision tree dict
        """
        tree = {
            'root': 'search',
            'nodes': [],
            'total_steps': len(trace)
        }
        
        for entry in trace:
            node = {
                'step': entry.get('step', 'unknown'),
                'timestamp': entry.get('timestamp'),
                'inputs': entry.get('inputs', {}),
                'outputs': entry.get('outputs', {}),
                'reasoning': entry.get('reasoning', ''),
                'metadata': {k: v for k, v in entry.items() 
                           if k not in ['step', 'timestamp', 'inputs', 'outputs', 'reasoning']}
            }
            tree['nodes'].append(node)
        
        return tree
    
    @staticmethod
    def explain_verdict(verdict: Dict, sources: List[Dict], trace: List[Dict]) -> str:
        """
        Generate textual explanation of verdict
        
        Args:
            verdict: Verdict dictionary
            sources: Sources list
            trace: Execution trace
            
        Returns:
            Markdown explanation
        """
        explanation = [
            f"# Explication du verdict: {verdict.get('verdict', 'N/A')}",
            f"\n**Confiance:** {verdict.get('confidence', 0)}%",
            f"\n## Processus de vérification\n",
        ]
        
        # Add trace steps
        for i, entry in enumerate(trace, 1):
            step_name = entry.get('step', 'unknown').replace('_', ' ').title()
            explanation.append(f"### {i}. {step_name}")
            
            if 'reasoning' in entry:
                explanation.append(f"_{entry['reasoning']}_\n")
            
            # Add specific info per step
            if entry.get('step') == 'search':
                explanation.append(f"- Sources trouvées: {entry.get('sources_found', 0)}")
            elif entry.get('step') == 'credibility':
                high_cred = entry.get('high_credibility_count', 0)
                explanation.append(f"- Sources haute crédibilité (≥0.7): {high_cred}")
            elif entry.get('step') == 'source_validation':
                explanation.append(f"- Action: {entry.get('action', 'N/A')}")
                explanation.append(f"- Sources conservées: {entry.get('kept_sources', 0)}")
            elif entry.get('step') == 'verdict':
                explanation.append(f"- Verdict: {entry.get('verdict_generated', 'N/A')}")
                explanation.append(f"- Confiance: {entry.get('confidence', 0)}%")
            
            explanation.append("")
        
        # Add sources analysis
        explanation.append("## Sources analysées\n")
        for i, src in enumerate(sources[:5], 1):
            cred_score = src.get('trust_score', 0)
            cred_emoji = "🟢" if cred_score >= 0.8 else "🟡" if cred_score >= 0.5 else "🔴"
            
            explanation.append(
                f"{i}. {cred_emoji} [{src.get('title', 'Sans titre')}]({src.get('url', '#')}) "
                f"(Crédibilité: {cred_score:.2f})"
            )
            
            if src.get('ai_analysis'):
                position = src['ai_analysis'].get('position', 'NEUTRE')
                explanation.append(f"   - Position: {position}")
        
        if len(sources) > 5:
            explanation.append(f"\n_...et {len(sources) - 5} autres sources_")
        
        return "\n".join(explanation)
    
    @staticmethod
    def export_trace_json(trace: List[Dict], filepath: str = None) -> str:
        """
        Export trace as JSON
        
        Args:
            trace: Trace list
            filepath: Optional file path to save
            
        Returns:
            JSON string
        """
        tree = DecisionTrace.generate_decision_tree(trace)
        json_str = json.dumps(tree, indent=2, ensure_ascii=False)
        
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json_str)
        
        return json_str

