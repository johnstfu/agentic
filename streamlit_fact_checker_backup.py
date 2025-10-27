# PATH: streamlit_fact_checker.py
"""
🔍 VÉRIFICATEUR DE FAITS - Interface Professionnelle
Design minimaliste, transparent et digne de confiance
Version française complète avec transparence technique maximale
"""

import streamlit as st
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import os
from dotenv import load_dotenv

# Import de l'agent intelligent
from smart_fact_checker import SmartFactChecker

# Charger les variables d'environnement
load_dotenv()

# Configuration de la page
st.set_page_config(
    page_title="Vérificateur de Faits",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="expanded"  # Expanded pour voir les options
)

# CSS MIT Media Lab - Minimaliste et professionnel
st.markdown("""
<style>
    /* Reset et base */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 800px;
    }
    
    /* Typography - MIT Style */
    .main-header {
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-size: 2.5rem;
        font-weight: 300;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 3rem;
        letter-spacing: -0.02em;
    }
    
    .subtitle {
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-size: 1.1rem;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 3rem;
        font-weight: 300;
    }
    
    /* Input area - Clean design */
    .stTextArea > div > div > textarea {
        border: 2px solid #ecf0f1;
        border-radius: 12px;
        padding: 1rem;
        font-size: 1rem;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        transition: all 0.3s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #3498db;
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
    }
    
    /* Button - MIT Style */
    .stButton > button {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 500;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
    }
    
    /* Verdict cards - Clean and trustworthy */
    .verdict-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        border: 1px solid #ecf0f1;
        transition: all 0.3s ease;
    }
    
    .verdict-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
    }
    
    .verdict-true {
        border-left: 4px solid #27ae60;
    }
    
    .verdict-false {
        border-left: 4px solid #e74c3c;
    }
    
    .verdict-uncertain {
        border-left: 4px solid #f39c12;
    }
    
    /* Confidence meter */
    .confidence-meter {
        background: #ecf0f1;
        border-radius: 20px;
        height: 8px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .confidence-fill {
        height: 100%;
        border-radius: 20px;
        transition: width 1s ease;
    }
    
    .confidence-true {
        background: linear-gradient(90deg, #27ae60, #2ecc71);
    }
    
    .confidence-false {
        background: linear-gradient(90deg, #e74c3c, #c0392b);
    }
    
    .confidence-uncertain {
        background: linear-gradient(90deg, #f39c12, #e67e22);
    }
    
    /* Source cards */
    .source-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #ecf0f1;
        transition: all 0.3s ease;
    }
    
    .source-card:hover {
        border-color: #3498db;
        box-shadow: 0 4px 16px rgba(52, 152, 219, 0.1);
    }
    
    .source-high {
        border-left: 4px solid #27ae60;
    }
    
    .source-medium {
        border-left: 4px solid #f39c12;
    }
    
    .source-low {
        border-left: 4px solid #e74c3c;
    }
    
    /* Loading animation */
    .loading-container {
        text-align: center;
        padding: 2rem;
    }
    
    .loading-spinner {
        width: 40px;
        height: 40px;
        border: 3px solid #ecf0f1;
        border-top: 3px solid #3498db;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 1rem;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom metrics */
    .metric-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        border: 1px solid #ecf0f1;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #7f8c8d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_agent():
    """Charge l'agent intelligent"""
    try:
        agent = SmartFactChecker()
        return agent, None
    except Exception as e:
        return None, str(e)


def create_confidence_meter(score):
    """Crée un mètre de véracité visuel"""
    if score >= 70:
        color_class = "confidence-true"
        interpretation = "VÉRIFIÉ"
    elif score >= 30:
        color_class = "confidence-uncertain"
        interpretation = "INCERTAIN"
    else:
        color_class = "confidence-false"
        interpretation = "CONTESTÉ"

    return f"""
    <div class="confidence-meter">
        <div class="confidence-fill {color_class}" style="width: {score}%"></div>
    </div>
    <div style="text-align: center; margin-top: 0.5rem;">
        <span style="font-weight: 600; color: #2c3e50;">{score}%</span>
        <span style="color: #7f8c8d; margin-left: 0.5rem;">{interpretation}</span>
    </div>
    """


def create_source_card(source, index):
    """Crée une carte de source élégante avec 4 niveaux de crédibilité"""
    trust_score = source.get('trust_score', 0.5)
    title = source.get('title', 'Untitled')
    url = source.get('url', '#')
    source_type = source.get('source_type', 'unknown')
    credibility_analysis = source.get('credibility_analysis', 'No analysis available')

    # Déterminer la classe CSS basée sur le score (4 niveaux stricts)
    if trust_score >= 0.85:
        card_class = "source-high"
        badge_color = "#27ae60"
        badge_text = "TRÈS HAUTE CRÉDIBILITÉ"
    elif trust_score >= 0.70:
        card_class = "source-high"
        badge_color = "#2ecc71"
        badge_text = "HAUTE CRÉDIBILITÉ"
    elif trust_score >= 0.50:
        card_class = "source-medium"
        badge_color = "#f39c12"
        badge_text = "CRÉDIBILITÉ MOYENNE"
    else:
        card_class = "source-low"
        badge_color = "#e74c3c"
        badge_text = "FAIBLE CRÉDIBILITÉ"
    
    return f"""
    <div class="source-card {card_class}">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
            <h4 style="margin: 0; color: #2c3e50; font-weight: 500;">{title}</h4>
            <span style="background: {badge_color}; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 500;">
                {badge_text}
            </span>
        </div>
        <p style="margin: 0.5rem 0; color: #7f8c8d; font-size: 0.9rem;">
            <strong>Type:</strong> {source_type.title()} | 
            <strong>Credibility:</strong> {trust_score:.2f}/1.0
        </p>
        <p style="margin: 0.5rem 0; color: #34495e; font-size: 0.9rem;">
            {credibility_analysis}
        </p>
        <a href="{url}" target="_blank" style="color: #3498db; text-decoration: none; font-size: 0.9rem;">
            View Source →
        </a>
    </div>
    """


def main():
    """Interface principale - MIT Media Lab Design"""
    
    # Header minimaliste
    st.markdown('<h1 class="main-header">FactChecker</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">AI-powered fact verification with transparent source analysis</p>', unsafe_allow_html=True)
    
    # Chargement de l'agent
    agent, error = load_agent()
    
    if error:
        st.error(f"**System Error:** {error}")
        st.info("Please check your API keys in the `.env` file.")
        return
    
    # Zone de saisie principale
    st.markdown("### What would you like to verify?")
    
    # Utiliser l'exemple si sélectionné
    default_text = st.session_state.get('last_claim', '')
    
    claim_text = st.text_area(
        "Claim to verify",
        value=default_text,
        placeholder="Enter a claim or statement to verify...",
        height=120,
        help="Enter any factual claim you'd like to verify using AI and web sources",
        label_visibility="collapsed"
    )
    
    # Bouton de vérification
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🔍 Verify Claim", type="primary", use_container_width=True):
            if not claim_text or not claim_text.strip():
                st.warning("Please enter a claim to verify.")
            elif len(claim_text.strip()) < 10:
                st.warning("Please enter a more detailed claim (minimum 10 characters).")
            else:
                # Affichage du loading
                with st.spinner(""):
                    st.markdown("""
                    <div class="loading-container">
                        <div class="loading-spinner"></div>
                        <p style="color: #7f8c8d; margin: 0;">Analyzing sources and verifying claim...</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    try:
                        # Appel à l'agent
                        result = agent.verify_claim(claim_text.strip())
                        
                        # Stockage du résultat
                        st.session_state['last_result'] = result
                        st.session_state['last_claim'] = claim_text.strip()
                        
                    except Exception as e:
                        st.error(f"**Analysis Error:** {str(e)}")
                        return
    
    # Affichage des résultats
    if 'last_result' in st.session_state:
        result = st.session_state['last_result']
        claim = st.session_state.get('last_claim', '')
        
        st.markdown("---")
        
        # Extraction des informations
        verdict = result.get('verdict', 'UNKNOWN')
        confidence = result.get('confidence', 50)
        raw_analysis = result.get('raw_analysis', 'No analysis available')
        sources = result.get('sources', [])
        
        # Détermination de la classe de verdict
        if "VÉRIFIÉ" in verdict and "NON" not in verdict:
            if "PARTIELLEMENT" in verdict:
                verdict_class = "verdict-uncertain"
                verdict_icon = "⚠️"
                verdict_text = "PARTIALLY VERIFIED"
            else:
                verdict_class = "verdict-true"
                verdict_icon = "✅"
                verdict_text = "VERIFIED"
        elif "NON VÉRIFIÉ" in verdict:
            verdict_class = "verdict-false"
            verdict_icon = "❌"
            verdict_text = "DISPUTED"
        else:
            verdict_class = "verdict-uncertain"
            verdict_icon = "⚠️"
            verdict_text = "UNCERTAIN"
        
        # Carte de verdict
        st.markdown(f"""
        <div class="verdict-card {verdict_class}">
            <div style="text-align: center;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">{verdict_icon}</div>
                <h2 style="margin: 0; color: #2c3e50; font-weight: 500;">{verdict_text}</h2>
                <p style="margin: 0.5rem 0; color: #7f8c8d;">"{claim}"</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Mètre de confiance
        st.markdown("### Confidence Level")
        st.markdown(create_confidence_meter(confidence), unsafe_allow_html=True)

        # Section Méthodologie (nouveau)
        with st.expander("📖 Methodology - How we evaluate credibility", expanded=False):
            st.markdown("""
            <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #3498db;">
                <h4 style="margin-top: 0; color: #2c3e50;">Credibility Scoring System (0.0-1.0)</h4>

                <p style="margin: 0.5rem 0;"><strong style="color: #27ae60;">0.95-1.0: VERY HIGH CREDIBILITY</strong></p>
                <p style="margin: 0 0 1rem 1rem; color: #555;">National governments (.gov, .gouv), WHO, UN, official EU institutions</p>

                <p style="margin: 0.5rem 0;"><strong style="color: #2ecc71;">0.85-0.94: HIGH CREDIBILITY</strong></p>
                <p style="margin: 0 0 1rem 1rem; color: #555;">Prestigious universities (.edu, .ac), Nature, Science, Lancet, recognized scientific institutions</p>

                <p style="margin: 0.5rem 0;"><strong style="color: #f39c12;">0.70-0.84: GOOD CREDIBILITY</strong></p>
                <p style="margin: 0 0 1rem 1rem; color: #555;">Established media (Reuters, BBC, AFP, AP, Le Monde), official organizations</p>

                <p style="margin: 0.5rem 0;"><strong style="color: #e67e22;">0.50-0.69: MEDIUM CREDIBILITY</strong></p>
                <p style="margin: 0 0 1rem 1rem; color: #555;">Recognized general media, regional scientific organizations</p>

                <p style="margin: 0.5rem 0;"><strong style="color: #e74c3c;">Below 0.50: LOW CREDIBILITY</strong></p>
                <p style="margin: 0 0 1rem 1rem; color: #555;">Unknown sources, personal blogs, unverified sites</p>

                <hr style="margin: 1.5rem 0; border: none; border-top: 1px solid #ddd;">

                <h4 style="margin-top: 1rem; color: #2c3e50;">Evaluation Criteria</h4>
                <ul style="color: #555; line-height: 1.8;">
                    <li><strong>Institution type:</strong> Government > Academic > Established media > Blog</li>
                    <li><strong>Historical reputation:</strong> Verifiable track record</li>
                    <li><strong>Domain expertise:</strong> Recognized expertise in the specific field</li>
                    <li><strong>Transparency:</strong> Clear methodology and editorial standards</li>
                    <li><strong>Independence:</strong> Absence of obvious conflicts of interest</li>
                </ul>

                <hr style="margin: 1.5rem 0; border: none; border-top: 1px solid #ddd;">

                <h4 style="margin-top: 1rem; color: #2c3e50;">Veracity Scoring (0-100%)</h4>
                <p style="color: #555; line-height: 1.6;">The veracity score represents how TRUE the claim is, based on the analysis of sources:</p>
                <ul style="color: #555; line-height: 1.8;">
                    <li><strong>81-100%:</strong> VERIFIED - Confirmed by multiple high-credibility sources (≥0.8)</li>
                    <li><strong>61-80%:</strong> PROBABLY TRUE - Majority of sources confirm</li>
                    <li><strong>41-60%:</strong> UNCERTAIN - Contradictory or insufficient sources</li>
                    <li><strong>21-40%:</strong> PROBABLY FALSE - Majority of sources dispute</li>
                    <li><strong>0-20%:</strong> DISPUTED - Confirmed as false by high-credibility sources</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        # Métriques
        stats = result.get('stats', {})
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{stats.get('total_sources', 0)}</div>
                <div class="metric-label">Sources</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{stats.get('high_credibility_sources', 0)}</div>
                <div class="metric-label">High Credibility</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{stats.get('sources_confirment', 0)}</div>
                <div class="metric-label">Confirm</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{stats.get('sources_infirment', 0)}</div>
                <div class="metric-label">Dispute</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Analyse détaillée - Version simplifiée
        st.markdown("### Analysis")
        
        # Extraction de l'analyse principale (sans les numéros)
        analysis_text = raw_analysis
        
        # Nettoyage de l'analyse pour UX
        if "ANALYSE DÉTAILLÉE:" in analysis_text:
            main_analysis = analysis_text.split("ANALYSE DÉTAILLÉE:")[1].split("SOURCES PAR POSITION:")[0].strip()
        else:
            main_analysis = analysis_text
        
        # Affichage de l'analyse principale
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #3498db; margin-bottom: 1rem;">
            <p style="margin: 0; line-height: 1.6; color: #2c3e50;">{main_analysis}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sources par position - Version simplifiée
        if "SOURCES PAR POSITION:" in analysis_text:
            sources_section = analysis_text.split("SOURCES PAR POSITION:")[1].split("RECOMMANDATION:")[0].strip()
            
            # Extraction des sources qui confirment/infirment
            confirm_sources = []
            dispute_sources = []
            
            if "CONFIRMENT:" in sources_section:
                confirm_part = sources_section.split("CONFIRMENT:")[1].split("INFIRMENT:")[0].strip()
                confirm_sources = [s.strip() for s in confirm_part.split('\n') if s.strip() and 'Source' in s]
            
            if "INFIRMENT:" in sources_section:
                dispute_part = sources_section.split("INFIRMENT:")[1].split("NEUTRES:")[0].strip()
                dispute_sources = [s.strip() for s in dispute_part.split('\n') if s.strip() and 'Source' in s]
            
            # Affichage des sources par position
            if confirm_sources or dispute_sources:
                st.markdown("### Source Positions")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if confirm_sources:
                        st.markdown("""
                        <div style="background: #d4edda; padding: 1rem; border-radius: 8px; border-left: 4px solid #27ae60;">
                            <h4 style="margin: 0 0 0.5rem 0; color: #155724;">✅ Sources that confirm</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        for source in confirm_sources[:3]:  # Limite à 3
                            st.markdown(f"• {source}")
                
                with col2:
                    if dispute_sources:
                        st.markdown("""
                        <div style="background: #f8d7da; padding: 1rem; border-radius: 8px; border-left: 4px solid #e74c3c;">
                            <h4 style="margin: 0 0 0.5rem 0; color: #721c24;">❌ Sources that dispute</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        for source in dispute_sources[:3]:  # Limite à 3
                            st.markdown(f"• {source}")
        
        # Recommandation simplifiée
        if "RECOMMANDATION:" in analysis_text:
            recommendation = analysis_text.split("RECOMMANDATION:")[1].strip()
            st.markdown("### Recommendation")
            st.info(f"💡 {recommendation}")
        
        # Sources - Version compacte avec seuil strict
        if sources:
            st.markdown("### Sources")

            # Affichage des sources les plus importantes d'abord (seuil strict: 0.85)
            very_high_cred_sources = [s for s in sources if s.get('trust_score', 0) >= 0.85]
            high_cred_sources = [s for s in sources if 0.7 <= s.get('trust_score', 0) < 0.85]
            other_sources = [s for s in sources if s.get('trust_score', 0) < 0.7]

            # Afficher d'abord les sources VERY HIGH (0.85+)
            displayed_count = 0
            for idx, source in enumerate(very_high_cred_sources, 1):
                if displayed_count < 3:  # Limite à 3 sources affichées
                    st.markdown(create_source_card(source, idx), unsafe_allow_html=True)
                    displayed_count += 1

            # Puis les sources HIGH (0.7-0.85) si besoin
            if displayed_count < 3:
                for idx, source in enumerate(high_cred_sources, len(very_high_cred_sources) + 1):
                    if displayed_count < 3:
                        st.markdown(create_source_card(source, idx), unsafe_allow_html=True)
                        displayed_count += 1
            
            # Bouton pour voir toutes les sources
            if len(sources) > 3:
                with st.expander(f"View all {len(sources)} sources", expanded=False):
                    for idx, source in enumerate(sources, 1):
                        st.markdown(create_source_card(source, idx), unsafe_allow_html=True)
        
        # Actions rapides
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📥 Export", use_container_width=True):
                json_str = json.dumps(result, ensure_ascii=False, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name=f"fact_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("📋 Copy", use_container_width=True):
                st.write("Copy functionality would be implemented here")
        
        with col3:
            if st.button("🔗 Share", use_container_width=True):
                st.write("Share functionality would be implemented here")
        
        with col4:
            if st.button("🔄 New Check", use_container_width=True):
                st.rerun()
    
    # Footer minimaliste
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #7f8c8d; padding: 2rem 0;">
        <p style="margin: 0; font-size: 0.9rem;">
            Powered by <strong>Tavily</strong> + <strong>OpenAI</strong> | 
            Transparent AI-powered fact verification
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()