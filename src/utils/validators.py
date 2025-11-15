"""
Input validation and sanitization utilities
"""

import re
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def sanitize_claim(claim: str) -> Optional[str]:
    """
    Nettoie et valide une affirmation utilisateur.
    
    Args:
        claim: Affirmation brute à valider
        
    Returns:
        Affirmation nettoyée si valide, None sinon
        
    Raises:
        None - Retourne None en cas d'erreur
        
    Example:
        >>> sanitize_claim("  La Tour Eiffel   mesure 330m  ")
        'La Tour Eiffel mesure 330m'
        >>> sanitize_claim("<script>alert('xss')</script>")
        None
    """
    if not claim or not isinstance(claim, str):
        logger.warning("Claim is empty or not a string")
        return None
    
    # Trim et normalise les espaces multiples
    clean = ' '.join(claim.strip().split())
    
    # Vérifie longueur (10-500 caractères)
    if len(clean) < 10:
        logger.warning(f"Claim too short: {len(clean)} chars (min 10)")
        return None
    
    if len(clean) > 500:
        logger.warning(f"Claim too long: {len(clean)} chars (max 500)")
        return None
    
    # Supprime caractères potentiellement dangereux
    # Garde lettres, chiffres, ponctuation basique, espaces
    clean = re.sub(r'[<>{}]', '', clean)
    
    # Vérifie qu'il reste du contenu après nettoyage
    if len(clean.strip()) < 10:
        logger.warning("Claim too short after sanitization")
        return None
    
    return clean


def validate_user_id(user_id: str) -> bool:
    """
    Valide un identifiant utilisateur.
    
    Args:
        user_id: ID utilisateur à valider
        
    Returns:
        True si valide, False sinon
        
    Example:
        >>> validate_user_id("user_123")
        True
        >>> validate_user_id("")
        False
    """
    if not user_id or not isinstance(user_id, str):
        return False
    
    # Alphanumerique + underscore, 3-50 caractères
    pattern = r'^[a-zA-Z0-9_]{3,50}$'
    return bool(re.match(pattern, user_id))


def sanitize_feedback_comment(comment: str) -> Optional[str]:
    """
    Nettoie un commentaire de feedback utilisateur.
    
    Args:
        comment: Commentaire brut
        
    Returns:
        Commentaire nettoyé si valide, None sinon
    """
    if not comment or not isinstance(comment, str):
        return None
    
    # Trim et normalise
    clean = ' '.join(comment.strip().split())
    
    # Max 1000 caractères pour commentaire
    if len(clean) > 1000:
        clean = clean[:1000]
    
    # Supprime HTML/scripts
    clean = re.sub(r'<[^>]+>', '', clean)
    
    return clean if clean else None

