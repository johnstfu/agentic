"""
UI component for viewing user history
"""

import streamlit as st
from typing import Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.persistence import PersistenceManager


def show_user_history(user_id: str, persistence: PersistenceManager):
    """
    Display user's fact-checking history
    
    Args:
        user_id: User identifier
        persistence: PersistenceManager instance
    """
    st.subheader("📜 Historique")
    
    try:
        history = persistence.get_user_history(user_id, limit=10)
        
        if not history:
            st.info("Aucun historique pour cet utilisateur")
            return
        
        st.caption(f"{len(history)} vérification(s) trouvée(s)")
        
        for i, item in enumerate(history):
            claim = item.get('claim', 'N/A')
            verdict_data = item.get('verdict', {})
            
            if isinstance(verdict_data, dict):
                verdict = verdict_data.get('verdict', 'N/A')
            else:
                verdict = 'N/A'
            
            timestamp = item.get('timestamp', 'N/A')
            
            # Emoji based on verdict
            if "✅" in str(verdict):
                emoji = "✅"
            elif "❌" in str(verdict):
                emoji = "❌"
            elif "⚠️" in str(verdict):
                emoji = "⚠️"
            else:
                emoji = "📄"
            
            with st.expander(f"{emoji} {claim[:40]}..."):
                st.caption(f"🕒 {timestamp}")
                st.markdown(f"**Verdict:** {verdict}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🔄 Réutiliser cette claim", key=f"reuse_{i}"):
                        st.session_state['claim'] = claim
                        st.rerun()
                
                with col2:
                    if st.button("📄 Voir détails", key=f"details_{i}"):
                        st.json(item)
    
    except Exception as e:
        st.error(f"Erreur lors du chargement de l'historique: {str(e)}")


def show_similar_claim_notification(similar: Optional[dict]):
    """
    Show notification if similar claim found
    
    Args:
        similar: Similar claim dict or None
    """
    if similar:
        st.info("💡 Une claim similaire a été trouvée dans votre historique")
        
        with st.expander("Voir la claim similaire"):
            st.markdown(f"**Claim:** {similar.get('claim', 'N/A')}")
            st.markdown(f"**Verdict:** {similar.get('verdict', {}).get('verdict', 'N/A')}")
            st.caption(f"Vérifié le: {similar.get('timestamp', 'N/A')}")
            
            if st.button("Utiliser ce résultat"):
                return similar
    
    return None

