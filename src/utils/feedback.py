"""
Feedback collection system for continuous improvement
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional


class FeedbackManager:
    """Manages user feedback collection and analysis"""
    
    def __init__(self, db_path: str = "feedback.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize feedback database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    claim TEXT NOT NULL,
                    verdict_given TEXT,
                    confidence_given INTEGER,
                    user_rating INTEGER CHECK(user_rating >= 1 AND user_rating <= 5),
                    user_comment TEXT,
                    correct_verdict TEXT,
                    timestamp TEXT,
                    flagged_for_review BOOLEAN DEFAULT 0
                )
            """)
            conn.commit()
    
    def collect_feedback(self, claim: str, verdict: Dict, user_feedback: Dict):
        """
        Collect user feedback
        
        Args:
            claim: The claim that was verified
            verdict: Verdict dictionary with verdict and confidence
            user_feedback: User's feedback with rating, comment, correct_verdict
        """
        with sqlite3.connect(self.db_path) as conn:
            # Detect divergence
            flagged = (
                user_feedback.get('correct_verdict') and
                user_feedback['correct_verdict'] != verdict.get('verdict', '')
            )
            
            conn.execute("""
                INSERT INTO feedback 
                (claim, verdict_given, confidence_given, user_rating, 
                 user_comment, correct_verdict, timestamp, flagged_for_review)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                claim,
                verdict.get('verdict', ''),
                verdict.get('confidence', 0),
                user_feedback.get('rating', 3),
                user_feedback.get('comment', ''),
                user_feedback.get('correct_verdict'),
                datetime.now().isoformat(),
                flagged
            ))
            conn.commit()
    
    def get_flagged_for_review(self, limit: int = 10) -> List[Dict]:
        """
        Get feedback flagged for review
        
        Args:
            limit: Maximum number of records
            
        Returns:
            List of flagged feedback
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM feedback 
                WHERE flagged_for_review = 1 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            columns = [c[0] for c in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_average_rating(self) -> float:
        """Get average user rating"""
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute("SELECT AVG(user_rating) FROM feedback").fetchone()
            return result[0] if result[0] is not None else 0.0
    
    def get_stats(self) -> Dict:
        """Get feedback statistics"""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]
            flagged = conn.execute("SELECT COUNT(*) FROM feedback WHERE flagged_for_review = 1").fetchone()[0]
            avg_rating = self.get_average_rating()
            
            return {
                'total_feedback': total,
                'flagged_count': flagged,
                'average_rating': avg_rating,
                'flagged_percentage': (flagged / total * 100) if total > 0 else 0
            }

