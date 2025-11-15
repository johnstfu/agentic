"""
UI components for handling Human-in-the-Loop interruptions
"""

import streamlit as st
from typing import Dict, Any, Optional


def handle_source_validation(interrupt_data: Dict) -> Optional[Dict]:
    """
    UI component for source validation
    
    Args:
        interrupt_data: Interrupt payload
        
    Returns:
        User response dict or None
    """
    st.warning("⏸️ VALIDATION REQUISE")
    st.markdown(f"### Claim: {interrupt_data['claim']}")
    
    action = st.radio("Action", [
        "Approuver toutes les sources",
        "Sélectionner manuellement",
        "Rejeter et reformuler"
    ], key="source_action")
    
    if action == "Sélectionner manuellement":
        st.markdown("### Cochez les sources à conserver:")
        selected = []
        
        for src in interrupt_data['sources_preview']:
            col1, col2 = st.columns([0.1, 0.9])
            with col1:
                if st.checkbox("", key=f"src_{src['index']}"):
                    selected.append(src['index'])
            with col2:
                st.markdown(f"**{src['title']}**")
                st.caption(f"🔗 {src['url']} | 📊 Tavily Score: {src['tavily_score']:.2f}")
                st.text(src['snippet'] + "...")
        
        if st.button("✅ Valider sélection", key="validate_selection"):
            if not selected:
                st.error("Veuillez sélectionner au moins une source")
                return None
            return {'action': 'select', 'selected_indices': selected}
    
    elif action == "Rejeter et reformuler":
        st.markdown("### Reformulez la recherche:")
        new_query = st.text_area(
            "Nouvelle requête",
            value=interrupt_data['claim'],
            key="reformulated_query"
        )
        
        if st.button("🔄 Relancer recherche", key="reformulate"):
            if not new_query.strip():
                st.error("La requête ne peut pas être vide")
                return None
            return {'action': 'reject_and_reformulate', 'reformulated_query': new_query}
    
    else:  # Approuver tout
        if st.button("✅ Approuver toutes les sources", key="approve_all"):
            return {'action': 'approve_all'}
    
    return None


def handle_verdict_review(interrupt_data: Dict) -> Optional[Dict]:
    """
    UI component for verdict review
    
    Args:
        interrupt_data: Interrupt payload
        
    Returns:
        User response dict or None
    """
    st.warning("⏸️ RÉVISION DU VERDICT")
    
    # Display generated verdict
    st.markdown("### Verdict généré par l'IA")
    
    verdict = interrupt_data['verdict']
    confidence = interrupt_data['confidence']
    
    if "✅" in verdict:
        st.success(f"**{verdict}** (Confiance: {confidence}%)")
    elif "❌" in verdict:
        st.error(f"**{verdict}** (Confiance: {confidence}%)")
    else:
        st.warning(f"**{verdict}** (Confiance: {confidence}%)")
    
    with st.expander("📄 Voir l'analyse complète"):
        st.markdown(interrupt_data['analysis'])
    
    # Display sources summary
    with st.expander(f"📚 Voir les {len(interrupt_data['sources'])} sources"):
        for i, src in enumerate(interrupt_data['sources'][:5], 1):
            st.markdown(f"**{i}. {src.get('title', 'N/A')}**")
            st.caption(f"Crédibilité: {src.get('trust_score', 0):.2f} | {src.get('url', 'N/A')}")
    
    # Action selection
    st.markdown("---")
    st.markdown("### Votre décision")
    
    action = st.radio("Action", ["Approuver", "Modifier", "Rejeter"], key="verdict_action")
    
    if action == "Modifier":
        col1, col2 = st.columns(2)
        
        with col1:
            new_verdict = st.selectbox("Nouveau verdict", [
                "✅ VÉRIFIÉ",
                "⚠️ PARTIELLEMENT VÉRIFIÉ",
                "❌ NON VÉRIFIÉ",
                "🔍 NÉCESSITE INVESTIGATION"
            ], key="new_verdict")
        
        with col2:
            new_confidence = st.slider(
                "Confiance (%)",
                0, 100, 
                confidence,
                key="new_confidence"
            )
        
        editor_note = st.text_area(
            "Note éditeur (sera visible dans le rapport)",
            placeholder="Expliquez pourquoi vous avez modifié le verdict...",
            key="editor_note"
        )
        
        if st.button("💾 Publier avec modifications", key="publish_edited"):
            if not editor_note.strip():
                st.error("Veuillez ajouter une note éditeur pour justifier la modification")
                return None
            
            return {
                'action': 'edit',
                'edited_verdict': new_verdict,
                'edited_confidence': new_confidence,
                'editor_note': editor_note
            }
    
    elif action == "Approuver":
        st.info("Le verdict sera publié tel quel")
        if st.button("✅ Publier le verdict", key="approve_verdict"):
            return {'action': 'approve'}
    
    else:  # Rejeter
        st.warning("L'analyse sera recommencée depuis le début")
        reason = st.text_input(
            "Raison du rejet (optionnel)",
            placeholder="Pourquoi rejeter ce verdict?",
            key="reject_reason"
        )
        
        if st.button("🔄 Refaire l'analyse", key="reject_verdict"):
            return {
                'action': 'reject',
                'reason': reason
            }
    
    return None


def handle_interrupt(interrupt_payload: Dict) -> Any:
    """
    Main router for all interrupt types
    
    Args:
        interrupt_payload: Interrupt data
        
    Returns:
        User response or None
    """
    interrupt_type = interrupt_payload.get('type')
    
    if interrupt_type == 'source_validation':
        return handle_source_validation(interrupt_payload)
    elif interrupt_type == 'verdict_review':
        return handle_verdict_review(interrupt_payload)
    else:
        st.error(f"❌ Type d'interruption inconnu: {interrupt_type}")
        return None

