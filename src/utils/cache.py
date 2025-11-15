"""
Système de cache pour éviter les requêtes répétées
"""
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional


class SimpleCache:
    """Cache simple en mémoire avec TTL"""

    def __init__(self, ttl_seconds: int = 3600):
        self.cache: Dict[str, dict] = {}
        self.ttl = ttl_seconds

    def _generate_key(self, claim: str) -> str:
        """Génère une clé unique pour le claim"""
        return hashlib.md5(claim.lower().strip().encode()).hexdigest()

    def get(self, claim: str) -> Optional[dict]:
        """Récupère un résultat du cache"""
        key = self._generate_key(claim)

        if key not in self.cache:
            return None

        entry = self.cache[key]

        # Vérifie si le cache est expiré
        if datetime.now() > entry['expires_at']:
            del self.cache[key]
            return None

        return entry['data']

    def set(self, claim: str, data: dict):
        """Stocke un résultat dans le cache"""
        key = self._generate_key(claim)

        self.cache[key] = {
            'data': data,
            'expires_at': datetime.now() + timedelta(seconds=self.ttl),
            'created_at': datetime.now()
        }

    def clear(self):
        """Vide le cache"""
        self.cache = {}

    def size(self) -> int:
        """Retourne le nombre d'entrées dans le cache"""
        return len(self.cache)
