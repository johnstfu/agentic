"""
Results display component for fact-checking interface
"""

import streamlit as st
import json
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, List
import re

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.config import Config


def _detect_sensitive_dates(sources: List[Dict], claim: str) -> List[str]:
    """
    Détecte si les sources ou la claim mentionnent des dates sensibles (poisson d'avril, etc.)
    
    Returns:
        Liste de warnings à afficher
    """
    warnings = []
    
    # Patterns pour détecter le 1er avril
    april_fools_patterns = [
        r'1er avril',
        r'premier avril',
        r'april 1',
        r'april fools',
        r'poisson d\'avril',
        r'1 avril',
        r'01/04',
        r'01-04',
        r'april 1st'
    ]
    
    # Vérifier dans la claim
    claim_lower = claim.lower()
    for pattern in april_fools_patterns:
        if re.search(pattern, claim_lower):
            warnings.append("🐟 **Alerte Poisson d'Avril** : Cette affirmation mentionne le 1er avril, date traditionnelle de canulars en France. Soyez particulièrement vigilant !")
            break
    
    # Vérifier dans les sources
    for source in sources[:3]:  # Check only first 3 sources
        content_lower = (source.get('title', '') + ' ' + source.get('content', '')).lower()
        for pattern in april_fools_patterns:
            if re.search(pattern, content_lower):
                warnings.append("🐟 **Date Sensible Détectée** : Une ou plusieurs sources mentionnent le 1er avril. Il pourrait s'agir d'un poisson d'avril (tradition française de canulars).")
                return warnings  # Return immediately to avoid duplicates
    
    return warnings


def display_verification_result(
    result: Dict,
    claim: str,
    is_v3: bool = False,
    min_credibility: float = 0.0,
    source_types: List[str] = None,
    feedback_mgr=None
):
    """
    Display verification result with verdict, analysis, sources and feedback.
    
    Args:
        result: Verification result dictionary
        claim: Original claim text
        is_v3: Whether result comes from v3.0 (LangGraph)
        min_credibility: Minimum credibility filter (not used, kept for compatibility)
        source_types: Source types filter (not used, kept for compatibility)
        feedback_mgr: FeedbackManager instance for collecting feedback
    """
    st.markdown("---")
    st.markdown("## 📋 Résultat de la Vérification")
    
    # Badge version et cache
    badges = []
    if is_v3:
        badges.append("🆕 v3.0 LangGraph")
    else:
        badges.append("🔹 v2.0 Stable")
    
    if result.get('from_cache', False):
        badges.append("💾 Depuis le cache")
    
    st.caption(" | ".join(badges))

    # Extract verdict data
    verdict_data = result.get('verdict', {}) if is_v3 else result
    verdict = verdict_data.get('verdict', 'INCONNU')
    confidence = verdict_data.get('confidence', 50)
    sources = verdict_data.get('sources', result.get('sources', []))

    # Determine verdict style
    if "VÉRIFIÉ" in verdict and "NON" not in verdict:
        if "PARTIELLEMENT" in verdict:
            verdict_class = "verdict-uncertain"
            verdict_icon = "⚠️"
            verdict_text = "PARTIELLEMENT VÉRIFIÉ"
        else:
            verdict_class = "verdict-true"
            verdict_icon = "✅"
            verdict_text = "VÉRIFIÉ"
    elif "NON VÉRIFIÉ" in verdict:
        verdict_class = "verdict-false"
        verdict_icon = "❌"
        verdict_text = "NON VÉRIFIÉ"
    else:
        verdict_class = "verdict-uncertain"
        verdict_icon = "⚠️"
        verdict_text = "INCERTAIN"

    # Display verdict card
    st.markdown(f"""
    <div class="verdict-card {verdict_class}">
        <div style="text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">{verdict_icon}</div>
            <h2 style="margin: 0; color: #2c3e50;">{verdict_text}</h2>
            <p style="margin: 0.5rem 0; color: #7f8c8d;">"{claim}"</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Détection dates sensibles (1er avril, etc.)
    date_warnings = _detect_sensitive_dates(sources, claim)
    if date_warnings:
        for warning in date_warnings:
            st.warning(warning)
    
    # Explanation legend
    with st.expander("💡 Comment interpréter ce résultat ?"):
        st.markdown("""
        **Niveaux de confiance :**
        - **80-100% :** Sources multiples et très fiables confirment l'information
        - **50-79% :** Information partiellement confirmée ou sources mixtes  
        - **0-49% :** Information contestée par les sources ou preuves insuffisantes
        
        **Verdicts possibles :**
        - ✅ **Vérifié :** L'affirmation est vraie selon plusieurs sources fiables
        - ⚠️ **Partiellement Vérifié :** Une partie est vraie, mais il manque du contexte
        - ❌ **Non Vérifié :** L'affirmation est fausse ou contredite
        - 🔍 **Nécessite Investigation :** Pas assez d'informations pour conclure
        """)

    # Confidence meter
    st.markdown("### 📊 Niveau de Confiance")
    _display_confidence_meter(confidence)

    # Stats
    stats = result.get('stats', {})
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📚 Sources", stats.get('total_sources', len(sources)))
    with col2:
        st.metric("⭐ Haute Créd.", stats.get('high_credibility_sources', 0))
    with col3:
        st.metric("✅ Confirment", stats.get('sources_confirment', 0))
    with col4:
        st.metric("❌ Contestent", stats.get('sources_infirment', 0))

    # Analysis
    st.markdown("### 🔍 Analyse Détaillée")
    st.caption("Explication du raisonnement de l'IA")
    
    # Extraire et nettoyer l'analyse
    raw_analysis = verdict_data.get('raw_analysis', result.get('raw_analysis', ''))
    
    # Parser l'analyse selon le format structuré
    main_analysis = raw_analysis
    if "3. ANALYSE DÉTAILLÉE:" in raw_analysis:
        # Extraire la section 3
        parts = raw_analysis.split("3. ANALYSE DÉTAILLÉE:")
        if len(parts) > 1:
            # Extraire jusqu'à la section 4
            analysis_section = parts[1].split("4.")[0].strip()
            main_analysis = analysis_section
    elif "ANALYSE DÉTAILLÉE:" in raw_analysis:
        # Fallback sans numéro
        parts = raw_analysis.split("ANALYSE DÉTAILLÉE:")
        if len(parts) > 1:
            analysis_section = parts[1].split("SOURCES PAR POSITION")[0].split("4.")[0].strip()
            main_analysis = analysis_section
    
    # Nettoyer le texte (retirer numéros résiduels, espaces multiples)
    import re
    main_analysis = re.sub(r'^\d+\.\s*', '', main_analysis)  # Retirer numéro au début
    main_analysis = re.sub(r'\s*\d+\.\s*$', '', main_analysis)  # Retirer numéro à la fin
    main_analysis = ' '.join(main_analysis.split())  # Normaliser espaces
    
    # Afficher dans un conteneur stylisé avec bonne lisibilité
    st.markdown(f"""
    <div style="background: #f0f7ff; 
                padding: 1.5rem; 
                border-radius: 12px; 
                border-left: 5px solid #3498db;
                box-shadow: 0 2px 8px rgba(52, 152, 219, 0.15);">
        <p style="color: #2c3e50; 
                  font-size: 1.15rem; 
                  line-height: 1.8; 
                  margin: 0;
                  font-weight: 400;">
            💬 {main_analysis}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Trace (v3 only)
    if is_v3 and 'trace' in result and result['trace']:
        _display_trace(result['trace'])

    # Sources
    if sources:
        _display_sources(sources)
    
    # Feedback section
    if feedback_mgr:
        _display_feedback_section(claim, verdict_data, feedback_mgr)

    # Logs (collapsed)
    with st.expander("🔧 Logs techniques (pour développeurs)"):
        logs = result.get('logs', [])
        if logs:
            for log in logs:
                st.text(log)
        else:
            st.info("Aucun log disponible")

    # Actions
    _display_actions(result, claim, main_analysis, sources)


def _display_confidence_meter(score: int):
    """Display confidence meter visualization"""
    if score >= 70:
        color_class = "confidence-true"
        color = "#27ae60"
        interpretation = "VRAI"
        display_score = score
        bar_width = score
    elif score >= 30:
        color_class = "confidence-uncertain"
        color = "#f39c12"
        interpretation = "INCERTAIN"
        display_score = score
        bar_width = score
    else:
        color_class = "confidence-false"
        color = "#e74c3c"
        interpretation = "FAUX"
        display_score = 100 - score
        bar_width = display_score

    st.markdown(f"""
    <div style="background: #ecf0f1; border-radius: 10px; overflow: hidden; height: 30px; position: relative;">
        <div style="background: {color}; width: {bar_width}%; height: 100%; transition: width 0.3s;"></div>
    </div>
    <div style="text-align: center; margin-top: 0.5rem;">
        <span style="font-weight: 600; color: #2c3e50; font-size: 1.2rem;">{display_score}%</span>
        <span style="color: #7f8c8d; margin-left: 0.5rem;">{interpretation}</span>
    </div>
    """, unsafe_allow_html=True)


def _display_trace(trace: List[Dict]):
    """Display execution trace for v3.0"""
    st.markdown("### 🔎 Processus de Vérification")
    st.caption("Étapes suivies par l'IA pour analyser cette affirmation")
    
    with st.expander("📊 Voir le processus détaillé"):
        for i, entry in enumerate(trace, 1):
            step_name = entry.get('step', 'N/A').replace('_', ' ').title()
            timestamp = entry.get('timestamp', 'N/A')
            
            st.markdown(f"**Étape {i} : {step_name}**")
            st.caption(f"⏱️ {timestamp}")
            
            if 'reasoning' in entry:
                st.info(entry['reasoning'])
            
            if entry.get('step') == 'search':
                sources_found = entry.get('sources_found', 0)
                st.success(f"✓ {sources_found} source(s) trouvée(s)")
            elif entry.get('step') == 'credibility':
                high_cred = entry.get('high_credibility_count', 0)
                st.success(f"✓ {high_cred} source(s) haute crédibilité")
            
            st.markdown("---")


def _display_sources(sources: List[Dict]):
    """Display sources list"""
    st.markdown("### 🔗 Sources Consultées")
    st.caption("Sources utilisées pour vérifier cette affirmation")

    # Filter to show all sources (min_credibility = 0.0)
    st.success(f"📊 {len(sources)} source(s) consultée(s)")

    # Show top 3
    for idx, source in enumerate(sources[:3], 1):
        _display_source_card(source, idx)

    # Expander for the rest
    if len(sources) > 3:
        with st.expander(f"📚 Voir les {len(sources)} sources complètes"):
            for idx, source in enumerate(sources, 1):
                _display_source_card(source, idx)


def _display_source_card(source: Dict, index: int):
    """Display individual source card"""
    trust_score = source.get('trust_score', 0.5)
    
    # Trust indicator
    if trust_score >= 0.7:
        trust_emoji = "🟢"
        trust_text = "Haute crédibilité"
        badge_color = "#27ae60"
    elif trust_score >= 0.4:
        trust_emoji = "🟡"
        trust_text = "Crédibilité moyenne"
        badge_color = "#f39c12"
    else:
        trust_emoji = "🔴"
        trust_text = "Crédibilité faible"
        badge_color = "#e74c3c"
    
    title = source.get('title', 'Sans titre')
    url = source.get('url', '#')
    source_type = source.get('source_type', 'unknown').title()
    
    st.markdown(f"""
    <div style="background: white; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; 
                border-left: 4px solid {badge_color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <h4 style="margin: 0; color: #2c3e50;">{trust_emoji} {title[:80]}{'...' if len(title) > 80 else ''}</h4>
        </div>
        <p style="margin: 0.5rem 0; color: #7f8c8d; font-size: 0.9rem;">
            <strong>Type:</strong> {source_type} | <strong>Score:</strong> {trust_score:.2f}/1.0 - {trust_text}
        </p>
        <a href="{url}" target="_blank" style="color: #3498db; text-decoration: none;">
            Voir la source →
        </a>
    </div>
    """, unsafe_allow_html=True)


def _display_feedback_section(claim: str, verdict_data: Dict, feedback_mgr):
    """Display feedback collection section"""
    st.markdown("---")
    st.markdown("### 💬 Donnez Votre Avis")
    st.caption("Aidez-nous à améliorer la qualité des vérifications")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        rating = st.slider("⭐ Qualité", 1, 5, 3, 
                         help="1 = Très mauvaise, 5 = Excellente")
    
    with col2:
        comment = st.text_area("💭 Commentaire (optionnel)", 
                               placeholder="Ex: Manque de sources récentes...",
                               height=100)
    
    # If user contests verdict
    verdict_wrong = st.checkbox("⚠️ Ce verdict me semble incorrect")
    correct_verdict = None
    if verdict_wrong:
        st.warning("📣 Merci de signaler cette erreur ! Un expert va réviser ce cas.")
        correct_verdict = st.selectbox("Selon vous, le bon verdict est :", [
            "✅ VÉRIFIÉ",
            "⚠️ PARTIELLEMENT VÉRIFIÉ",
            "❌ NON VÉRIFIÉ",
            "🔍 NÉCESSITE INVESTIGATION"
        ])
    
    st.markdown("")  # Espace
    if st.button("📤 Envoyer mon avis", type="primary", use_container_width=True, key="send_feedback"):
        try:
            feedback_mgr.collect_feedback(
                claim=claim,
                verdict=verdict_data,
                user_feedback={
                    'rating': rating,
                    'comment': comment,
                    'correct_verdict': correct_verdict
                }
            )
            st.success("✅ Merci ! Votre retour va nous aider à améliorer le service.")
            if verdict_wrong:
                st.info("🔔 Ce cas a été signalé à notre équipe pour révision humaine.")
        except Exception as e:
            st.error(f"❌ Erreur lors de l'envoi : {str(e)}")


def _display_actions(result: Dict, claim: str, analysis: str, sources: List):
    """Display action buttons"""
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📥 Exporter", use_container_width=True):
            json_str = json.dumps(result, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 Télécharger JSON",
                data=json_str,
                file_name=f"verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

    with col2:
        if st.button("🔄 Nouvelle vérification", use_container_width=True, type="primary"):
            for key in ['last_result', 'last_claim', 'use_v3']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    with col3:
        if st.button("📋 Copier résumé", use_container_width=True):
            summary = f"""Vérification : {claim}
Verdict : {result.get('verdict', {}).get('verdict', 'N/A')}
Confiance : {result.get('verdict', {}).get('confidence', 0)}%
Analyse : {analysis[:200]}...
Sources : {len(sources)} consultée(s)"""
            st.code(summary, language="text")
            st.caption("💡 Sélectionnez et copiez le texte ci-dessus")

