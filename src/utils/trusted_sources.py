"""
Whitelist des sources fiables pour fact-checking
Scoring basé sur la fiabilité et l'autorité des domaines
"""

from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import re


# Tier 1 : Sources gouvernementales & institutions internationales (Score: 0.95)
TIER1_GOVERNMENT = {
    'score': 0.95,
    'domains': [
        # France
        'gouv.fr', 'service-public.fr', 'legifrance.gouv.fr', 'insee.fr',
        'data.gouv.fr', 'vie-publique.fr', 'assemblee-nationale.fr', 'senat.fr',
        
        # Europe
        'europa.eu', 'europarl.europa.eu', 'ecb.europa.eu', 'ecdc.europa.eu',
        
        # International (ONU & affiliés)
        'un.org', 'who.int', 'unicef.org', 'unesco.org', 'unhcr.org',
        'wmo.int', 'iaea.org', 'fao.org',
        
        # USA
        'cdc.gov', 'nasa.gov', 'usgs.gov', 'noaa.gov', 'nih.gov',
        
        # Autres pays
        'gov.uk', 'nhs.uk', 'canada.ca', 'admin.ch', 'bundesregierung.de',
    ],
    'description': 'Sources gouvernementales officielles et organisations internationales'
}

# Tier 2 : Académique & Scientifique (Score: 0.90)
TIER2_ACADEMIC = {
    'score': 0.90,
    'domains': [
        # Journals scientifiques
        'nature.com', 'science.org', 'cell.com', 'thelancet.com', 'nejm.org',
        'bmj.com', 'sciencedirect.com', 'plos.org',
        
        # Bases de données
        'pubmed.ncbi.nlm.nih.gov', 'scholar.google.com', 'arxiv.org',
        'researchgate.net', 'hal.archives-ouvertes.fr',
        
        # Institutions françaises
        'cnrs.fr', 'inria.fr', 'inserm.fr', 'cea.fr', 'cnes.fr',
        'pasteur.fr', 'ined.fr', 'ird.fr',
        
        # Universités (pattern .edu, .ac)
        'mit.edu', 'stanford.edu', 'harvard.edu', 'ox.ac.uk', 'cam.ac.uk',
        'eth.ch', 'epfl.ch',
        
        # Think tanks
        'brookings.edu', 'rand.org', 'carnegieendowment.org', 'ifri.org',
    ],
    'description': 'Recherche académique et publications scientifiques'
}

# Tier 3 : Fact-Checking Spécialisé (Score: 0.88)
TIER3_FACTCHECKERS = {
    'score': 0.88,
    'domains': [
        # France
        'lemonde.fr/les-decodeurs', 'liberation.fr/checknews', 'afp.com/fr/afp-factuel',
        
        # International
        'factcheck.org', 'snopes.com', 'politifact.com', 'fullfact.org',
        'apnews.com/ap-fact-check', 'reuters.com/fact-check',
        'climatefeedback.org',
    ],
    'description': 'Organisations spécialisées en vérification de faits'
}

# Tier 4 : Agences de presse & Médias premium (Score: 0.82)
TIER4_PREMIUM_MEDIA = {
    'score': 0.82,
    'domains': [
        # Agences de presse
        'reuters.com', 'apnews.com', 'afp.com', 'dpa.com',
        
        # Presse française qualité
        'lemonde.fr', 'lefigaro.fr', 'lesechos.fr', 'mediapart.fr',
        'courrierinternational.com', 'monde-diplomatique.fr',
        
        # International
        'bbc.com', 'bbc.co.uk', 'theguardian.com', 'nytimes.com',
        'washingtonpost.com', 'wsj.com', 'ft.com', 'economist.com',
        
        # Médias spécialisés
        'france24.com', 'rfi.fr', 'arte.tv', 'francetvinfo.fr',
    ],
    'description': 'Médias établis avec standards éditoriaux rigoureux'
}

# Tier 5 : Encyclopédies (Score: 0.78)
TIER5_ENCYCLOPEDIAS = {
    'score': 0.78,
    'domains': [
        'wikipedia.org', 'britannica.com', 'larousse.fr', 'universalis.fr',
        'wikimedia.org', 'wiktionary.org',
    ],
    'description': 'Encyclopédies collaboratives et éditoriales'
}

# Tier 6 : Organisations spécialisées (Score: 0.85)
TIER6_SPECIALIZED = {
    'score': 0.85,
    'domains': [
        # Climat
        'ipcc.ch', 'climate.nasa.gov',
        
        # Santé
        'mayoclinic.org', 'cochrane.org', 'cancer.org',
        
        # Espace
        'esa.int', 'spacex.com', 'jaxa.jp',
        
        # Économie
        'imf.org', 'worldbank.org', 'oecd.org', 'wto.org',
        
        # Droits humains
        'amnesty.org', 'hrw.org', 'icrc.org',
        
        # Environnement
        'unep.org', 'iucn.org', 'wwf.org',
    ],
    'description': 'Organisations spécialisées reconnues'
}

# Blacklist : Sources à éviter
BLACKLIST = [
    '4chan.org', '8kun.top', 'parler.com', 'gab.com',
    'infowars.com', 'breitbart.com', 'naturalnews.com',
    'globalresearch.ca', 'zerohedge.com',
    # Réseaux sociaux (pas sources primaires)
    'facebook.com', 'twitter.com', 'x.com', 'instagram.com', 'tiktok.com',
]

# Compilation de tous les tiers
ALL_TIERS = {
    'tier1': TIER1_GOVERNMENT,
    'tier2': TIER2_ACADEMIC,
    'tier3': TIER3_FACTCHECKERS,
    'tier4': TIER4_PREMIUM_MEDIA,
    'tier5': TIER5_ENCYCLOPEDIAS,
    'tier6': TIER6_SPECIALIZED,
}


def get_domain_from_url(url: str) -> str:
    """Extrait le domaine principal d'une URL"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Retirer www.
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return ''


def get_source_tier(url: str) -> Optional[str]:
    """
    Identifie le tier d'une source selon son URL
    
    Args:
        url: URL de la source
        
    Returns:
        Nom du tier (tier1-tier6) ou None si non trouvé
    """
    domain = get_domain_from_url(url)
    if not domain:
        return None
    
    # Vérifier blacklist d'abord
    if any(blocked in domain for blocked in BLACKLIST):
        return 'blacklisted'
    
    # Vérifier chaque tier
    for tier_name, tier_data in ALL_TIERS.items():
        for trusted_domain in tier_data['domains']:
            if trusted_domain in domain or domain.endswith(trusted_domain):
                return tier_name
    
    # Pattern matching pour domaines académiques génériques
    if re.search(r'\.(edu|ac\.uk|ac\.[a-z]{2})($|/)', url):
        return 'tier2'  # Académique
    
    return None


def get_domain_base_score(url: str) -> float:
    """
    Retourne le score de base d'un domaine selon la whitelist
    
    Args:
        url: URL de la source
        
    Returns:
        Score 0.0-1.0, ou 0.5 par défaut si non trouvé
    """
    tier = get_source_tier(url)
    
    if tier == 'blacklisted':
        return 0.1  # Score très bas pour sources blacklistées
    
    if tier and tier in ALL_TIERS:
        return ALL_TIERS[tier]['score']
    
    # Domaine inconnu = score moyen/faible
    return 0.5


def get_tier_description(tier_name: str) -> str:
    """Retourne la description d'un tier"""
    if tier_name in ALL_TIERS:
        return ALL_TIERS[tier_name]['description']
    return "Source non classée"


def is_trusted_domain(url: str, min_tier_score: float = 0.75) -> bool:
    """
    Vérifie si un domaine est considéré comme fiable
    
    Args:
        url: URL à vérifier
        min_tier_score: Score minimum pour être considéré fiable
        
    Returns:
        True si fiable, False sinon
    """
    score = get_domain_base_score(url)
    return score >= min_tier_score


def get_priority_domains_for_topic(claim: str) -> List[str]:
    """
    Retourne les domaines prioritaires selon le sujet de la claim
    
    Args:
        claim: Affirmation à vérifier
        
    Returns:
        Liste de domaines prioritaires
    """
    claim_lower = claim.lower()
    
    # Santé
    if any(word in claim_lower for word in ['vaccin', 'médicament', 'maladie', 'santé', 'covid', 'virus']):
        return ['who.int', 'pubmed.ncbi.nlm.nih.gov', 'cdc.gov', 'pasteur.fr', 'inserm.fr']
    
    # Politique française
    elif any(word in claim_lower for word in ['gouvernement', 'loi', 'président', 'élection', 'assemblée', 'sénat']):
        return ['gouv.fr', 'vie-publique.fr', 'assemblee-nationale.fr', 'lemonde.fr', 'liberation.fr']
    
    # Science
    elif any(word in claim_lower for word in ['étude', 'recherche', 'scientifique', 'expérience']):
        return ['nature.com', 'science.org', 'cnrs.fr', 'arxiv.org', 'wikipedia.org']
    
    # Géographie/Histoire
    elif any(word in claim_lower for word in ['tour eiffel', 'capitale', 'pays', 'ville', 'monument', 'situé']):
        return ['wikipedia.org', 'britannica.com', 'larousse.fr', 'gouv.fr']
    
    # Climat/Environnement
    elif any(word in claim_lower for word in ['climat', 'réchauffement', 'environnement', 'co2', 'température']):
        return ['ipcc.ch', 'climate.nasa.gov', 'unep.org', 'nature.com']
    
    # International
    elif any(word in claim_lower for word in ['onu', 'international', 'mondial', 'guerre']):
        return ['un.org', 'unesco.org', 'who.int', 'reuters.com', 'afp.com']
    
    # Défaut : sources encyclopédiques + fact-checkers
    else:
        return ['wikipedia.org', 'lemonde.fr/les-decodeurs', 'factcheck.org', 'britannica.com']


def calculate_trust_score(url: str, llm_analysis: Optional[str] = None) -> float:
    """
    Calcule le score de confiance final d'une source
    
    Combine:
    - Score de base (whitelist)
    - Analyse LLM (si disponible)
    
    Args:
        url: URL de la source
        llm_analysis: Analyse optionnelle du LLM
        
    Returns:
        Score final 0.0-1.0
    """
    # Score de base
    base_score = get_domain_base_score(url)
    
    # Si pas d'analyse LLM, retourner score de base
    if not llm_analysis:
        return base_score
    
    # Bonus/malus basé sur analyse LLM (simplifié)
    analysis_lower = llm_analysis.lower()
    
    # Bonus
    if any(word in analysis_lower for word in ['fiable', 'crédible', 'officiel', 'reconnu']):
        base_score = min(1.0, base_score + 0.05)
    
    # Malus
    if any(word in analysis_lower for word in ['douteux', 'peu fiable', 'controversé', 'biais']):
        base_score = max(0.0, base_score - 0.10)
    
    return round(base_score, 2)

