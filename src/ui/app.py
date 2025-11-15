"""
🔍 VÉRIFICATEUR DE FAITS - Interface Streamlit v2.0 + v3.0
Design professionnel avec agent amélioré et support LangGraph
"""

import streamlit as st
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import agents (v2 and v3)
from agents.fact_checker import SmartFactChecker  # v2.0
from agents.fact_checker_graph import FactCheckerGraph  # v3.0
from utils.config import Config
from utils.feedback import FeedbackManager
from utils.explainability import DecisionTrace
from utils.validators import sanitize_claim

# Import UI components
from ui.components import interrupt_handler, history_viewer
from ui.components.results_display import display_verification_result

# Import LangGraph
from langgraph.types import Command

# Configuration de la page
st.set_page_config(
    page_title=Config.APP_NAME,
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Import CSS depuis fichier externe
CSS_FILE = os.path.join(os.path.dirname(__file__), 'styles.css')
if os.path.exists(CSS_FILE):
    with open(CSS_FILE) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
else:
    # CSS inline minimal si fichier absent
    st.markdown("""
    <style>
        .main .block-container {max-width: 800px; padding-top: 2rem;}
        .main-header {font-size: 2.5rem; text-align: center; color: #2c3e50; margin-bottom: 2rem;}
        .verdict-card {background: white; border-radius: 16px; padding: 2rem; margin: 1.5rem 0; box-shadow: 0 8px 32px rgba(0,0,0,0.08);}
    </style>
    """, unsafe_allow_html=True)


@st.cache_resource
def load_agent_v2():
    """Charge l'agent v2.0 avec cache"""
    try:
        agent = SmartFactChecker(enable_cache=Config.ENABLE_CACHE)
        return agent, None
    except Exception as e:
        return None, str(e)

@st.cache_resource
def load_agent_v3(enable_hitl: bool = True):
    """Charge l'agent v3.0 (LangGraph)"""
    try:
        agent = FactCheckerGraph(enable_hitl=enable_hitl, enable_cache=Config.ENABLE_CACHE)
        return agent, None
    except Exception as e:
        return None, str(e)

@st.cache_resource
def load_feedback_manager():
    """Charge le gestionnaire de feedback"""
    try:
        return FeedbackManager(Config.FEEDBACK_DB)
    except Exception as e:
        st.error(f"Erreur chargement feedback: {e}")
        return None


def filter_sources_by_criteria(sources, min_credibility, source_types):
    """Filtre les sources selon les critères"""
    filtered = []
    for source in sources:
        if source.get('trust_score', 0) < min_credibility:
            continue

        if "all" not in source_types:
            if source.get('source_type', 'unknown') not in source_types:
                continue

        filtered.append(source)

    return filtered


def create_confidence_meter(score):
    """Crée un mètre de véracité visuel"""
    if score >= 70:
        color_class = "confidence-true"
        interpretation = "VRAI"
        display_score = score
        bar_width = score
    elif score >= 30:
        color_class = "confidence-uncertain"
        interpretation = "INCERTAIN"
        display_score = score
        bar_width = score
    else:
        color_class = "confidence-false"
        interpretation = "FAUX"
        display_score = 100 - score
        bar_width = display_score

    return f"""
    <div class="confidence-meter">
        <div class="confidence-fill {color_class}" style="width: {bar_width}%"></div>
    </div>
    <div style="text-align: center; margin-top: 0.5rem;">
        <span style="font-weight: 600; color: #2c3e50;">{display_score}%</span>
        <span style="color: #7f8c8d; margin-left: 0.5rem;">{interpretation}</span>
    </div>
    """


def create_source_card(source, index):
    """Crée une carte de source"""
    trust_score = source.get('trust_score', 0.5)
    title = source.get('title', 'Sans titre')
    url = source.get('url', '#')
    source_type = source.get('source_type', 'unknown')
    credibility_analysis = source.get('credibility_analysis', 'Aucune analyse')

    if trust_score >= 0.85:
        card_class = "source-high"
        badge_color = "#27ae60"
        badge_text = "TRÈS HAUTE CRÉDIBILITÉ"
        stars = "★★★★★"
    elif trust_score >= 0.70:
        card_class = "source-high"
        badge_color = "#2ecc71"
        badge_text = "HAUTE CRÉDIBILITÉ"
        stars = "★★★★"
    elif trust_score >= 0.50:
        card_class = "source-medium"
        badge_color = "#f39c12"
        badge_text = "CRÉDIBILITÉ MOYENNE"
        stars = "★★★"
    else:
        card_class = "source-low"
        badge_color = "#e74c3c"
        badge_text = "FAIBLE CRÉDIBILITÉ"
        stars = "★★"

    return f"""
    <div class="source-card {card_class}">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
            <h4 style="margin: 0; color: #2c3e50;">{title}</h4>
            <span style="background: {badge_color}; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem;">
                {badge_text}
            </span>
        </div>
        <p style="margin: 0.5rem 0; color: #7f8c8d; font-size: 0.9rem;">
            <strong>Type:</strong> {source_type.title()} | <strong>Score:</strong> {trust_score:.2f}/1.0 {stars}
        </p>
        <p style="margin: 0.5rem 0; color: #34495e;">{credibility_analysis}</p>
        <a href="{url}" target="_blank" style="color: #3498db; text-decoration: none;">
            Voir la source →
        </a>
    </div>
    """


def main():
    """Interface principale - Support v2.0 et v3.0"""

    # Sidebar - Version Selection
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Version selector
        if Config.ENABLE_VERSION_SELECTOR:
            version = st.radio(
                "Version du fact-checker",
                ["v2.0 (Stable)", "v3.0 (LangGraph + HITL)"],
                index=1 if Config.DEFAULT_VERSION == "v3.0" else 0,
                help="v2.0 = ancien système, v3.0 = nouveau avec interruptions humaines"
            )
            use_v3 = "v3.0" in version
        else:
            use_v3 = Config.DEFAULT_VERSION == "v3.0"
        
        # v3.0 specific options
        enable_hitl = False
        user_id = "default"
        mode = "Simple"
        
        if use_v3:
            st.success("✨ Fonctionnalités v3.0 activées")
            
            enable_hitl = st.checkbox(
                "🤖 Activer Human-in-the-Loop",
                value=False,  # Désactivé par défaut pour éviter l'erreur DB
                help="Mode expert : validez manuellement les sources et verdicts"
            )
            
            mode = st.radio(
                "📦 Mode de vérification",
                ["Simple", "Batch"],
                help="Simple = une affirmation / Batch = plusieurs affirmations"
            )
        
        # Valeurs fixes (pas de filtres compliqués)
        min_credibility = 0.0  # Afficher toutes les sources
        source_types = ["all"]

        # Informations simplifiées
        st.markdown("---")
        version_display = "v3.0 LangGraph" if use_v3 else "v2.0 Stable"
        st.caption(f"Version: {version_display} | Modèle: {Config.OPENAI_MODEL}")

    # Header
    st.markdown(f'<h1 class="main-header">{Config.APP_NAME}</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #7f8c8d;">Vérification de faits par IA avec analyse transparente</p>', unsafe_allow_html=True)

    # Chargement de l'agent selon version
    if use_v3:
        agent, error = load_agent_v3(enable_hitl)
    else:
        agent, error = load_agent_v2()

    if error:
        st.error(f"**Erreur système:** {error}")
        st.info("💡 Veuillez vérifier vos clés API dans le fichier `.env`")
        st.info("Consultez le README.md pour plus d'informations")
        return

    # Load feedback manager
    feedback_mgr = load_feedback_manager()

    # MODE BATCH (v3.0 uniquement)
    if mode == "Batch" and use_v3:
        st.markdown("### 📦 Vérification par Lot")
        st.info("💡 Entrez plusieurs affirmations (une par ligne, maximum 10)")
        
        batch_text = st.text_area(
            "Affirmations à vérifier",
            height=200,
            placeholder="Exemple:\nLa Tour Eiffel mesure 330 mètres\nParis est la capitale de la France\nLe Soleil tourne autour de la Terre",
            help="Entrez une affirmation par ligne"
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            batch_verify = st.button("🔍 Vérifier tout", type="primary", use_container_width=True)
        
        if batch_verify:
            # Validate and sanitize each claim
            raw_claims = [c.strip() for c in batch_text.split('\n') if c.strip()]
            claims = [sanitize_claim(c) for c in raw_claims]
            claims = [c for c in claims if c]  # Remove None values
            
            if not claims:
                st.warning("⚠️ Veuillez entrer au moins une affirmation valide")
            elif len(claims) != len(raw_claims):
                st.warning(f"⚠️ {len(raw_claims) - len(claims)} affirmation(s) invalide(s) ignorée(s)")
            elif len(claims) > Config.BATCH_MAX_CLAIMS:
                st.error(f"❌ Maximum {Config.BATCH_MAX_CLAIMS} affirmations par lot")
            else:
                with st.spinner(f"🔄 Vérification de {len(claims)} affirmation(s) en cours..."):
                    try:
                        batch_result = agent.verify_batch(claims, user_id=user_id)
                        st.session_state['batch_result'] = batch_result
                    except Exception as e:
                        st.error(f"❌ **Erreur:** {str(e)}")
                        return
        
        # Affichage résultats batch
        if 'batch_result' in st.session_state:
            batch_result = st.session_state['batch_result']
            
            st.markdown("---")
            st.markdown("## 📊 Résultats de la Vérification par Lot")
            
            # Statistiques globales
            stats = batch_result['stats']
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📝 Total", stats['total'])
            with col2:
                st.metric("✅ Vérifié", stats['verified'])
            with col3:
                st.metric("❌ Rejeté", stats['rejected'])
            with col4:
                st.metric("⚠️ Incertain", stats['uncertain'])
            
            # Graphique comparatif
            st.markdown("### 📈 Scores de Confiance")
            fig = go.Figure(data=[
                go.Bar(
                    x=[r['claim'][:30] + '...' if len(r['claim']) > 30 else r['claim'] 
                       for r in batch_result['results']],
                    y=[r.get('result', {}).get('verdict', {}).get('confidence', 0) 
                       for r in batch_result['results']],
                    marker_color=[
                        'green' if r.get('result', {}).get('verdict', {}).get('confidence', 0) >= 70
                        else 'orange' if r.get('result', {}).get('verdict', {}).get('confidence', 0) >= 30
                        else 'red'
                        for r in batch_result['results']
                    ],
                    text=[f"{r.get('result', {}).get('verdict', {}).get('confidence', 0)}%" 
                          for r in batch_result['results']],
                    textposition='auto',
                )
            ])
            fig.update_layout(
                title="Niveau de confiance par affirmation",
                yaxis_title="Confiance (%)",
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Détails par claim
            st.markdown("### 📋 Résultats Détaillés")
            for i, r in enumerate(batch_result['results'], 1):
                with st.expander(f"{i}. {r['claim'][:60]}{'...' if len(r['claim']) > 60 else ''}"):
                    if 'result' in r:
                        result_data = r['result']
                        verdict_data = result_data.get('verdict', {})
                        
                        st.markdown(f"**Verdict:** {verdict_data.get('verdict', 'N/A')}")
                        st.markdown(f"**Confiance:** {verdict_data.get('confidence', 0)}%")
                        
                        analysis = verdict_data.get('raw_analysis', '')
                        if analysis:
                            st.markdown("**Analyse:**")
                            st.text(analysis[:500] + ('...' if len(analysis) > 500 else ''))
                    else:
                        st.error(f"❌ Erreur: {r.get('error', 'Erreur inconnue')}")
            
            # Actions
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Exporter les résultats", use_container_width=True):
                    json_str = json.dumps(batch_result, ensure_ascii=False, indent=2)
                    st.download_button(
                        label="Télécharger JSON",
                        data=json_str,
                        file_name=f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
            with col2:
                if st.button("🔄 Nouvelle vérification", use_container_width=True):
                    del st.session_state['batch_result']
                    st.rerun()
        
        return  # Stop here for batch mode
    
    # MODE SIMPLE (v2.0 et v3.0)
    st.markdown("### 💬 Que souhaitez-vous vérifier ?")
    st.caption("Entrez une affirmation et nous allons vérifier sa véracité avec des sources fiables")

    claim_text = st.text_area(
        "Affirmation à vérifier",
        value=st.session_state.get('last_claim', ''),
        placeholder="Exemple: La Tour Eiffel mesure 330 mètres de hauteur",
        height=120,
        label_visibility="collapsed",
        help="Entrez une affirmation factuelle que vous souhaitez vérifier"
    )

    # Bouton de vérification
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        verify_clicked = st.button("🔍 Vérifier cette affirmation", type="primary", use_container_width=True)

    if verify_clicked:
        # Validate and sanitize input
        claim = sanitize_claim(claim_text)
        
        if not claim:
            st.warning("⚠️ Veuillez entrer une affirmation valide (10-500 caractères, sans caractères spéciaux)")
        else:
            
            # v3.0 avec HITL
            if use_v3 and enable_hitl:
                st.info("🤖 Mode Human-in-the-Loop activé : vous pourrez valider les sources et le verdict")
                
                config = {"configurable": {"thread_id": f"{user_id}_{datetime.now().timestamp()}"}}
                
                with st.spinner("🔍 Recherche de sources en cours..."):
                    try:
                        result = agent.graph.invoke({
                            "claim": claim,
                            "user_id": user_id,
                            "trace": [],
                            "timestamp": datetime.now().isoformat()
                        }, config)
                    except Exception as e:
                        st.error(f"❌ **Erreur:** {str(e)}")
                        return
                
                # Gestion des interruptions
                max_iterations = 10
                iteration = 0
                
                while '__interrupt__' in result and iteration < max_iterations:
                    iteration += 1
                    
                    interrupt_data = result['__interrupt__'][0].value
                    st.markdown("---")
                    
                    # Appel du handler d'interruption
                    user_response = interrupt_handler.handle_interrupt(interrupt_data)
                    
                    if user_response:
                        with st.spinner("⏳ Traitement de votre réponse..."):
                            try:
                                result = agent.graph.invoke(
                                    Command(resume=user_response),
                                    config
                                )
                            except Exception as e:
                                st.error(f"❌ **Erreur:** {str(e)}")
                                return
                    else:
                        st.info("⏸️ En attente de votre validation...")
                        st.stop()
                
                if iteration >= max_iterations:
                    st.error("❌ Trop d'itérations, processus arrêté")
                    return
                
                # Format result for display
                st.session_state['last_result'] = agent._format_result(result)
                st.session_state['last_claim'] = claim
                st.session_state['use_v3'] = True
                st.rerun()
            
            # v3.0 sans HITL ou v2.0
            else:
                with st.spinner("🔍 Analyse en cours..."):
                    try:
                        if use_v3:
                            result = agent.verify(claim, user_id=user_id)
                            st.session_state['use_v3'] = True
                        else:
                            result = agent.verify_claim(claim)
                            st.session_state['use_v3'] = False
                        
                        st.session_state['last_result'] = result
                        st.session_state['last_claim'] = claim
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ **Erreur:** {str(e)}")
                        return

    # Affichage des résultats
    if 'last_result' in st.session_state:
        result = st.session_state['last_result']
        claim = st.session_state.get('last_claim', '')
        is_v3 = st.session_state.get('use_v3', False)
        
        # Use refactored display component
        display_verification_result(
            result=result,
            claim=claim,
            is_v3=is_v3,
            min_credibility=min_credibility,
            source_types=source_types,
            feedback_mgr=feedback_mgr
        )

    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #7f8c8d; padding: 2rem 0;">
        <p style="margin: 0;">
            {Config.APP_NAME} v{Config.APP_VERSION} | Propulsé par Tavily + OpenAI
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
