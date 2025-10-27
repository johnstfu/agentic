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
import time

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


def filter_sources_by_criteria(sources, min_credibility, source_types):
    """Filtre les sources selon les critères sélectionnés"""
    filtered = []
    for source in sources:
        # Filtre par crédibilité minimale
        if source.get('trust_score', 0) < min_credibility:
            continue

        # Filtre par type (si pas "all")
        if "all" not in source_types:
            if source.get('source_type', 'unknown') not in source_types:
                continue

        filtered.append(source)

    return filtered


def create_confidence_meter(score):
    """Crée un mètre de véracité visuel avec inversion pour fake news (Option A)"""

    # Logique d'affichage selon le score
    if score >= 70:
        # Score élevé = VRAI
        color_class = "confidence-true"
        interpretation = "VRAI"
        display_score = score
        bar_width = score
    elif score >= 30:
        # Score moyen = INCERTAIN
        color_class = "confidence-uncertain"
        interpretation = "INCERTAIN"
        display_score = score
        bar_width = score
    else:
        # Score faible = FAUX (on inverse l'affichage)
        color_class = "confidence-false"
        interpretation = "FAUX"
        display_score = 100 - score  # Inversion : 5% → affiche 95%
        bar_width = display_score  # La barre montre le niveau de certitude que c'est faux

    return f"""
    <div class="confidence-meter">
        <div class="confidence-fill {color_class}" style="width: {bar_width}%"></div>
    </div>
    <div style="text-align: center; margin-top: 0.5rem;">
        <span style="font-weight: 600; color: #2c3e50;">{display_score}%</span>
        <span style="color: #7f8c8d; margin-left: 0.5rem;">{interpretation}</span>
    </div>
    <div style="text-align: center; margin-top: 0.25rem; font-size: 0.85rem; color: #95a5a6;">
        {"Certitude que l'affirmation est FAUSSE" if score < 30 else "Certitude que l'affirmation est VRAIE" if score >= 70 else "Niveau d'incertitude"}
    </div>
    """


def create_source_card(source, index, show_timestamp=True):
    """Crée une carte de source élégante avec 4 niveaux de crédibilité"""
    trust_score = source.get('trust_score', 0.5)
    title = source.get('title', 'Sans titre')
    url = source.get('url', '#')
    source_type = source.get('source_type', 'unknown')
    credibility_analysis = source.get('credibility_analysis', 'Aucune analyse disponible')

    # Déterminer la classe CSS basée sur le score (4 niveaux stricts)
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

    # Timestamp de vérification
    timestamp_html = ""
    if show_timestamp:
        timestamp_html = f'<p style="margin: 0.5rem 0; color: #95a5a6; font-size: 0.8rem;">📅 Dernière vérification: {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>'

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
            <strong>Crédibilité:</strong> {trust_score:.2f}/1.0 {stars}
        </p>
        <p style="margin: 0.5rem 0; color: #34495e; font-size: 0.9rem;">
            {credibility_analysis}
        </p>
        {timestamp_html}
        <a href="{url}" target="_blank" style="color: #3498db; text-decoration: none; font-size: 0.9rem;">
            Voir la source →
        </a>
    </div>
    """


def main():
    """Interface principale - MIT Media Lab Design"""

    # SIDEBAR - Paramètres et informations
    with st.sidebar:
        st.header("⚙️ Paramètres & Informations")

        # Section Filtres - Version améliorée
        st.subheader("🔍 Filtres de sources")

        # Curseur avec annotations détaillées
        min_credibility = st.slider(
            "Crédibilité minimale affichée",
            0.0, 1.0, 0.5, 0.05,
            help="""
            **Échelle de crédibilité** :

            • 0.95-1.0 : Gouvernements (.gov, .gouv), OMS, ONU, UE
            • 0.85-0.95 : Universités prestigieuses, revues scientifiques (Nature, Science)
            • 0.70-0.85 : Médias établis (BBC, Reuters, AFP, Le Monde)
            • 0.50-0.70 : Médias généralistes, organisations régionales
            • < 0.50 : Sources peu connues, non vérifiées

            **Astuce** : Les médias établis ont généralement un score de 0.70-0.85
            """
        )

        # Annotation visuelle du curseur
        if min_credibility >= 0.95:
            st.caption("🏛️ Filtrage : Institutions officielles uniquement (≥0.95)")
        elif min_credibility >= 0.85:
            st.caption("🎓 Filtrage : Sources scientifiques et institutionnelles (≥0.85)")
        elif min_credibility >= 0.70:
            st.caption("📰 Filtrage : Médias établis et sources fiables (≥0.70)")
        elif min_credibility >= 0.50:
            st.caption("📊 Filtrage : Sources reconnues minimum (≥0.50)")
        else:
            st.caption("🌐 Filtrage : Toutes les sources (≥{:.2f})".format(min_credibility))

        source_types = st.multiselect(
            "Types de sources",
            ["government", "academic", "media", "all"],
            default=["all"],
            help="""
            **Types de sources** :

            • government : Sources gouvernementales (≥0.95)
            • academic : Sources académiques/scientifiques (≥0.85)
            • media : Médias et presse (généralement 0.60-0.85)
            • all : Tous les types

            **Note** : Si vous combinez "government" avec un curseur ≥0.85, seules les sources ≥0.95 s'afficheront.
            """
        )

        # Section Timestamps et infos techniques
        st.subheader("📅 Dernière actualisation")
        current_time = datetime.now().strftime('%d/%m/%Y %H:%M')
        st.info(f"""
**Modèle IA:** GPT-4 Turbo
**Moteur de recherche:** Tavily (temps réel)
**Date d'analyse:** {current_time}
        """)

        # Section Méthodologie complète
        with st.expander("📊 Méthodologie de scoring", expanded=False):
            st.markdown("""
### 🎯 SYSTÈME DE PONDÉRATION DES SOURCES

**Scoring de crédibilité (0.0 à 1.0)**:

• **0.95-1.0 (★★★★★) INSTITUTIONS OFFICIELLES**
  *Pondération: ×3.0*
  Gouvernements (.gov, .gouv), OMS, ONU, UE officielles

• **0.85-0.94 (★★★★) SOURCES SCIENTIFIQUES RECONNUES**
  *Pondération: ×2.5*
  Universités prestigieuses, Nature, Science, Lancet

• **0.70-0.84 (★★★) MÉDIAS ÉTABLIS HAUTE RÉPUTATION**
  *Pondération: ×2.0*
  Reuters, BBC, AFP, AP, Le Monde

• **0.50-0.69 (★★) MÉDIAS RECONNUS**
  *Pondération: ×1.5*
  Médias généralistes, organisations régionales

• **< 0.50 (★) SOURCES À VÉRIFIER**
  *Pondération: ×1.0*
  Sources peu connues, non vérifiées

---

**Calcul du score de véracité**:

```
Score final = Σ(score_source × pondération_source) / Σ(pondérations)
```

Les sources institutionnelles (≥0.85) ont **2-3× plus de poids** dans le calcul final.

**Interprétation du score de véracité (0-100%)**:
- **81-100%**: VÉRIFIÉ - Confirmé par sources haute crédibilité
- **61-80%**: PROBABLEMENT VRAI - Majorité confirme
- **41-60%**: INCERTAIN - Sources contradictoires
- **21-40%**: PROBABLEMENT FAUX - Majorité conteste
- **0-20%**: CONTESTÉ - Confirmé faux par sources fiables
            """)

        # Politique de confidentialité
        with st.expander("🔒 Confidentialité & Sécurité"):
            st.markdown("""
**Traitement des données**:
- ✅ Aucune donnée personnelle collectée
- ✅ Requêtes analysées en temps réel
- ✅ Aucun stockage permanent
- ✅ Communication chiffrée (HTTPS)
- ✅ Conforme RGPD

**Technologies utilisées**:
- OpenAI GPT-4 Turbo (analyse)
- Tavily Search API (recherche web)
- Streamlit (interface)
            """)

    # Header minimaliste
    st.markdown('<h1 class="main-header">VérificateurIA</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Vérification de faits par IA avec analyse transparente des sources</p>', unsafe_allow_html=True)

    # Chargement de l'agent
    agent, error = load_agent()

    if error:
        st.error(f"**Erreur système:** {error}")
        st.info("Veuillez vérifier vos clés API dans le fichier `.env`.")
        return
    
    # Zone de saisie principale
    st.markdown("### Que souhaitez-vous vérifier ?")

    # Utiliser l'exemple si sélectionné
    default_text = st.session_state.get('last_claim', '')

    claim_text = st.text_area(
        "Affirmation à vérifier",
        value=default_text,
        placeholder="Entrez une affirmation ou déclaration à vérifier...",
        height=120,
        help="Entrez n'importe quelle affirmation factuelle que vous souhaitez vérifier grâce à l'IA et aux sources web",
        label_visibility="collapsed"
    )

    # Bouton de vérification
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        verify_clicked = st.button("🔍 Vérifier l'affirmation", type="primary", use_container_width=True)

    if verify_clicked:
        if not claim_text or not claim_text.strip():
            st.warning("Veuillez entrer une affirmation à vérifier.")
        elif len(claim_text.strip()) < 10:
            st.warning("Veuillez entrer une affirmation plus détaillée (minimum 10 caractères).")
        else:
            # Initialisation des timestamps et métriques techniques
            start_time = time.time()
            st.session_state['analysis_start_time'] = datetime.now()

            # Affichage du loading
            with st.spinner(""):
                st.markdown("""
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <p style="color: #7f8c8d; margin: 0;">Analyse des sources et vérification en cours...</p>
                </div>
                """, unsafe_allow_html=True)

                try:
                    # Appel à l'agent avec mesure du temps
                    result = agent.verify_claim(claim_text.strip())

                    # Calcul du temps de traitement
                    end_time = time.time()
                    processing_time = end_time - start_time

                    # Stockage du résultat avec métriques techniques
                    result['technical_metrics'] = {
                        'processing_time': processing_time,
                        'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                        'model_used': 'GPT-4 Turbo',
                        'search_engine': 'Tavily API'
                    }

                    st.session_state['last_result'] = result
                    st.session_state['last_claim'] = claim_text.strip()

                except Exception as e:
                    st.error(f"**Erreur d'analyse:** {str(e)}")
                    return
    
    # Affichage des résultats
    if 'last_result' in st.session_state:
        result = st.session_state['last_result']
        claim = st.session_state.get('last_claim', '')

        st.markdown("---")

        # Extraction des informations
        verdict = result.get('verdict', 'INCONNU')
        confidence = result.get('confidence', 50)
        raw_analysis = result.get('raw_analysis', 'Aucune analyse disponible')
        sources = result.get('sources', [])
        technical_metrics = result.get('technical_metrics', {})

        # Timestamp de l'analyse
        analysis_timestamp = technical_metrics.get('timestamp', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))

        # Détermination de la classe de verdict
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
            verdict_text = "CONTESTÉ"
        else:
            verdict_class = "verdict-uncertain"
            verdict_icon = "⚠️"
            verdict_text = "INCERTAIN"

        # Carte de verdict avec timestamp
        st.markdown(f"""
        <div class="verdict-card {verdict_class}">
            <div style="text-align: center;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">{verdict_icon}</div>
                <h2 style="margin: 0; color: #2c3e50; font-weight: 500;">{verdict_text}</h2>
                <p style="margin: 0.5rem 0; color: #7f8c8d;">"{claim}"</p>
                <p style="margin: 1rem 0 0 0; color: #95a5a6; font-size: 0.85rem;">
                    📅 Analyse effectuée le: {analysis_timestamp}
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Mètre de confiance
        st.markdown("### Niveau de véracité")
        st.markdown(create_confidence_meter(confidence), unsafe_allow_html=True)

        # Logs techniques visibles
        with st.expander("🔧 Détails techniques de l'analyse", expanded=False):
            processing_time = technical_metrics.get('processing_time', 0)
            model_used = technical_metrics.get('model_used', 'N/A')
            search_engine = technical_metrics.get('search_engine', 'N/A')

            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #3498db;">
                <h4 style="margin-top: 0; color: #2c3e50;">📊 Métriques de performance</h4>

                <p style="margin: 0.5rem 0; color: #555;">
                    <strong>Temps de traitement total:</strong> {processing_time:.2f} secondes
                </p>
                <p style="margin: 0.5rem 0; color: #555;">
                    <strong>Modèle IA utilisé:</strong> {model_used}
                </p>
                <p style="margin: 0.5rem 0; color: #555;">
                    <strong>Moteur de recherche:</strong> {search_engine}
                </p>
                <p style="margin: 0.5rem 0; color: #555;">
                    <strong>Nombre de sources analysées:</strong> {len(sources)}
                </p>
                <p style="margin: 0.5rem 0; color: #555;">
                    <strong>Timestamp:</strong> {analysis_timestamp}
                </p>

                <hr style="margin: 1rem 0; border: none; border-top: 1px solid #ddd;">

                <h4 style="margin-top: 1rem; color: #2c3e50;">🔍 Détails de la recherche</h4>
                <p style="margin: 0.5rem 0; color: #555;">
                    Sources haute crédibilité (≥0.85): {len([s for s in sources if s.get('trust_score', 0) >= 0.85])}
                </p>
                <p style="margin: 0.5rem 0; color: #555;">
                    Sources moyenne crédibilité (0.50-0.84): {len([s for s in sources if 0.50 <= s.get('trust_score', 0) < 0.85])}
                </p>
                <p style="margin: 0.5rem 0; color: #555;">
                    Sources faible crédibilité (&lt;0.50): {len([s for s in sources if s.get('trust_score', 0) < 0.50])}
                </p>
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
                <div class="metric-label">Haute Crédibilité</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{stats.get('sources_confirment', 0)}</div>
                <div class="metric-label">Confirment</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{stats.get('sources_infirment', 0)}</div>
                <div class="metric-label">Contestent</div>
            </div>
            """, unsafe_allow_html=True)

        # Analyse détaillée - Version simplifiée
        st.markdown("### Analyse")
        
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
                st.markdown("### Position des sources")

                col1, col2 = st.columns(2)

                with col1:
                    if confirm_sources:
                        st.markdown("""
                        <div style="background: #d4edda; padding: 1rem; border-radius: 8px; border-left: 4px solid #27ae60;">
                            <h4 style="margin: 0 0 0.5rem 0; color: #155724;">✅ Sources qui confirment</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        for source in confirm_sources[:3]:  # Limite à 3
                            st.markdown(f"• {source}")

                with col2:
                    if dispute_sources:
                        st.markdown("""
                        <div style="background: #f8d7da; padding: 1rem; border-radius: 8px; border-left: 4px solid #e74c3c;">
                            <h4 style="margin: 0 0 0.5rem 0; color: #721c24;">❌ Sources qui contestent</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        for source in dispute_sources[:3]:  # Limite à 3
                            st.markdown(f"• {source}")

        # Recommandation simplifiée
        if "RECOMMANDATION:" in analysis_text:
            recommendation = analysis_text.split("RECOMMANDATION:")[1].strip()
            st.markdown("### Recommandation")
            st.info(f"💡 {recommendation}")
        
        # Sources - Version compacte avec filtres et compteur dynamique
        if sources:
            st.markdown("### Sources")

            # Application des filtres de la sidebar
            filtered_sources = filter_sources_by_criteria(sources, min_credibility, source_types)

            # Compteur dynamique de sources
            total_sources = len(sources)
            filtered_count = len(filtered_sources)

            # Affichage du compteur avec style visuel
            if filtered_count < total_sources:
                st.info(f"📊 **{filtered_count} sources affichées sur {total_sources}** (filtrage actif : crédibilité ≥ {min_credibility:.2f})")
            else:
                st.success(f"📊 **{total_sources} sources affichées** (aucun filtrage actif)")

            # Affichage des sources filtrées par ordre de crédibilité
            very_high_cred_sources = [s for s in filtered_sources if s.get('trust_score', 0) >= 0.85]
            high_cred_sources = [s for s in filtered_sources if 0.7 <= s.get('trust_score', 0) < 0.85]
            other_sources = [s for s in filtered_sources if s.get('trust_score', 0) < 0.7]

            # Affichage d'un message si les filtres excluent toutes les sources
            if not filtered_sources:
                st.warning(f"""
                ⚠️ **Aucune source ne correspond aux critères de filtrage**

                Crédibilité minimale : {min_credibility:.2f}
                Types sélectionnés : {', '.join(source_types)}

                **Suggestions** :
                - Réduisez le curseur de crédibilité minimale (actuellement {min_credibility:.2f})
                - Ajoutez "all" dans les types de sources
                - Les médias établis (BBC, Reuters, AFP) ont généralement un score de 0.70-0.85
                """)
            else:
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

                # Bouton pour voir toutes les sources filtrées
                if len(filtered_sources) > 3:
                    with st.expander(f"Voir les {len(filtered_sources)} sources ({len(sources)} au total)", expanded=False):
                        for idx, source in enumerate(filtered_sources, 1):
                            st.markdown(create_source_card(source, idx), unsafe_allow_html=True)
        
        # Actions rapides
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("📥 Exporter", use_container_width=True):
                json_str = json.dumps(result, ensure_ascii=False, indent=2)
                st.download_button(
                    label="Télécharger JSON",
                    data=json_str,
                    file_name=f"verification_faits_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

        with col2:
            if st.button("📋 Copier", use_container_width=True):
                st.info("Fonctionnalité de copie en développement")

        with col3:
            if st.button("🔗 Partager", use_container_width=True):
                st.info("Fonctionnalité de partage en développement")

        with col4:
            if st.button("🔄 Nouvelle vérification", use_container_width=True):
                st.rerun()

    # Footer minimaliste
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #7f8c8d; padding: 2rem 0;">
        <p style="margin: 0; font-size: 0.9rem;">
            Propulsé par <strong>Tavily</strong> + <strong>OpenAI</strong> |
            Vérification de faits par IA transparente
        </p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem;">
            Version française complète | Dernière mise à jour: Octobre 2025
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()