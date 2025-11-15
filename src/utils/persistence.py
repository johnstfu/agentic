"""
Persistence manager for fact-checking sessions using LangGraph SqliteSaver
"""

from langgraph.checkpoint.sqlite import SqliteSaver
from typing import List, Dict, Optional
import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PersistenceManager:
    """Manages persistence of fact-checking sessions"""
    
    def __init__(self, db_path: str = "fact_checks.db"):
        self.db_path = db_path
        # Create direct SQLite connection instead of using context manager
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.checkpointer = SqliteSaver(conn=self.conn)
    
    def get_user_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        Get user's fact-checking history
        
        Args:
            user_id: User identifier
            limit: Maximum number of records
            
        Returns:
            List of fact-check sessions
        """
        try:
            history = []
            
            # Query checkpoints for this user
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT thread_id, checkpoint_id, metadata, channel_values
                    FROM checkpoints
                    WHERE thread_id LIKE ?
                    ORDER BY checkpoint_id DESC
                    LIMIT ?
                """, (f"%{user_id}%", limit * 3))  # Get more to filter duplicates
                
                seen_threads = set()
                for row in cursor.fetchall():
                    thread_id, checkpoint_id, metadata, channel_values = row
                    
                    # Skip duplicates (keep only latest checkpoint per thread)
                    if thread_id in seen_threads:
                        continue
                    seen_threads.add(thread_id)
                    
                    try:
                        # Parse channel_values to extract claim info
                        import json
                        values = json.loads(channel_values) if channel_values else {}
                        
                        if 'claim' in values:
                            history.append({
                                'thread_id': thread_id,
                                'claim': values.get('claim', 'N/A'),
                                'verdict': values.get('verdict', {}),
                                'timestamp': values.get('timestamp', datetime.now().isoformat())
                            })
                            
                            if len(history) >= limit:
                                break
                    except:
                        continue
            
            return history
        
        except Exception as e:
            logger.error(f"Error getting user history: {e}", exc_info=True)
            return []
    
    def find_similar_claims(self, claim: str, user_id: str, threshold: float = 0.8) -> Optional[Dict]:
        """
        Find similar claims already verified
        
        Args:
            claim: Claim to search for
            user_id: User identifier
            threshold: Similarity threshold
            
        Returns:
            Similar claim dict or None
        """
        history = self.get_user_history(user_id, limit=20)
        
        # Simple similarity check (can be improved with embeddings)
        claim_lower = claim.lower()
        for item in history:
            item_claim = item.get('claim', '').lower()
            
            # Basic fuzzy match
            if len(item_claim) > 0:
                words_claim = set(claim_lower.split())
                words_item = set(item_claim.split())
                
                if len(words_claim) > 0:
                    overlap = len(words_claim & words_item) / len(words_claim)
                    
                    if overlap >= threshold:
                        return item
        
        return None
    
    def close(self):
        """Close database connection properly"""
        if hasattr(self, 'conn') and self.conn:
            try:
                self.conn.close()
                logger.debug(f"Closed connection to {self.db_path}")
            except Exception as e:
                logger.error(f"Error closing connection: {e}", exc_info=True)
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close()

