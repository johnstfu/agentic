# PATH: fact_checker_agent.py
"""
🔍 FACT-CHECKER AGENT - Vérificateur de Véracité avec Sources Officielles
Conçu pour Cursor Agent Mode Auto
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from urllib.parse import urlparse
import hashlib

# Core dependencies
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

# LangChain imports
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import Tool, StructuredTool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import SystemMessage, HumanMessage
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# For Cursor Agent compatibility
from dataclasses import dataclass
from enum import Enum


# ============================================
# CONFIGURATION
# ============================================

class Config:
    """Configuration centralisée pour l'agent"""
    
    # API Keys (à configurer dans .env ou directement)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-key-here")
    
    # Sources officielles de confiance (extensible)
    TRUSTED_SOURCES = {
        # Gouvernement FR
        "gouvernement.fr": {"score": 10, "type": "government"},
        "service-public.fr": {"score": 10, "type": "government"},
        "legifrance.gouv.fr": {"score": 10, "type": "legal"},
        
        # Organisations internationales
        "who.int": {"score": 9, "type": "health"},
        "un.org": {"score": 9, "type": "international"},
        "europa.eu": {"score": 9, "type": "government"},
        
        # Institutions scientifiques
        "nature.com": {"score": 8, "type": "scientific"},
        "science.org": {"score": 8, "type": "scientific"},
        "pubmed.ncbi.nlm.nih.gov": {"score": 9, "type": "medical"},
        
        # Fact-checkers reconnus
        "snopes.com": {"score": 7, "type": "factcheck"},
        "factcheck.org": {"score": 7, "type": "factcheck"},
        "politifact.com": {"score": 7, "type": "factcheck"},
        
        # Médias de référence
        "reuters.com": {"score": 6, "type": "news"},
        "apnews.com": {"score": 6, "type": "news"},
        "bbc.com": {"score": 6, "type": "news"},
        
        # Encyclopédies
        "britannica.com": {"score": 7, "type": "encyclopedia"},
        "wikipedia.org": {"score": 5, "type": "encyclopedia"},
    }
    
    # Headers pour les requêtes
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Paramètres de l'agent
    MODEL_NAME = "gpt-4-turbo-preview"
    MAX_SEARCH_RESULTS = 5
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200


# ============================================
# MODÈLES DE DONNÉES
# ============================================

class VerificationStatus(Enum):
    """Statuts de vérification"""
    VERIFIED = "✅ VÉRIFIÉ"
    PARTIALLY_VERIFIED = "⚠️ PARTIELLEMENT VÉRIFIÉ"
    UNVERIFIED = "❌ NON VÉRIFIÉ"
    CONTRADICTORY = "🔄 CONTRADICTOIRE"
    INSUFFICIENT_DATA = "❓ DONNÉES INSUFFISANTES"


@dataclass
class FactClaim:
    """Représente une affirmation à vérifier"""
    claim: str
    source: Optional[str] = None
    date: Optional[str] = None
    context: Optional[str] = None


@dataclass
class SourceEvidence:
    """Preuve trouvée dans une source"""
    url: str
    domain: str
    trust_score: float
    content: str
    supports_claim: bool
    confidence: float
    extraction_date: str


@dataclass
class VerificationResult:
    """Résultat complet de vérification"""
    claim: FactClaim
    status: VerificationStatus
    confidence_score: float
    official_sources: List[SourceEvidence]
    other_sources: List[SourceEvidence]
    analysis: str
    recommendations: List[str]


# ============================================
# OUTILS DE SCRAPING ET ANALYSE
# ============================================

class WebScraper:
    """Outil de scraping web intelligent"""
    
    @staticmethod
    def scrape_url(url: str) -> Dict[str, Any]:
        """Scrape une URL et extrait le contenu pertinent"""
        try:
            response = requests.get(url, headers=Config.HEADERS, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Supprime scripts et styles
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extraction du texte principal
            text = soup.get_text(separator=' ', strip=True)
            
            # Métadonnées
            title = soup.find('title').text if soup.find('title') else ''
            meta_desc = ''
            if soup.find('meta', {'name': 'description'}):
                meta_desc = soup.find('meta', {'name': 'description'}).get('content', '')
            
            return {
                "url": url,
                "title": title,
                "description": meta_desc,
                "content": text[:5000],  # Limite pour l'efficacité
                "success": True
            }
            
        except Exception as e:
            return {
                "url": url,
                "error": str(e),
                "success": False
            }
    
    @staticmethod
    def search_google(query: str, num_results: int = 5) -> List[str]:
        """Recherche Google (simulée - remplacer par API réelle en prod)"""
        # Pour Cursor : utilise DuckDuckGo comme alternative
        try:
            from duckduckgo_search import DDGS
            
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=num_results))
                return [r['href'] for r in results]
        except:
            # Fallback : URLs de démo
            return [
                f"https://example.com/result_{i}" 
                for i in range(num_results)
            ]


class TrustAnalyzer:
    """Analyse la fiabilité des sources"""
    
    @staticmethod
    def calculate_trust_score(url: str) -> Tuple[float, str]:
        """Calcule un score de confiance pour une URL"""
        domain = urlparse(url).netloc.lower()
        
        # Vérifie les sources officielles
        for trusted_domain, info in Config.TRUSTED_SOURCES.items():
            if trusted_domain in domain:
                return info['score'] / 10.0, info['type']
        
        # Score par défaut pour sources non listées
        if '.gov' in domain or '.gouv' in domain:
            return 0.8, 'government'
        elif '.edu' in domain or '.ac.' in domain:
            return 0.7, 'academic'
        elif '.org' in domain:
            return 0.5, 'organization'
        else:
            return 0.3, 'unknown'
    
    @staticmethod
    def extract_relevant_content(text: str, claim: str) -> str:
        """Extrait le contenu pertinent par rapport à la claim"""
        # Tokenisation simple
        claim_words = set(claim.lower().split())
        sentences = text.split('.')
        
        relevant_sentences = []
        for sentence in sentences:
            sentence_words = set(sentence.lower().split())
            # Score de pertinence basique
            overlap = len(claim_words & sentence_words)
            if overlap > 2:  # Seuil de pertinence
                relevant_sentences.append(sentence.strip())
        
        return '. '.join(relevant_sentences[:10])  # Max 10 phrases


# ============================================
# OUTILS LANGCHAIN
# ============================================

def create_fact_checking_tools():
    """Crée les outils pour l'agent LangChain"""
    
    def search_and_scrape(query: str) -> str:
        """Recherche et scrape des informations sur le web"""
        scraper = WebScraper()
        urls = scraper.search_google(query, Config.MAX_SEARCH_RESULTS)
        
        results = []
        for url in urls:
            data = scraper.scrape_url(url)
            if data['success']:
                trust_score, source_type = TrustAnalyzer.calculate_trust_score(url)
                results.append({
                    'url': url,
                    'title': data['title'],
                    'content': data['content'][:500],
                    'trust_score': trust_score,
                    'source_type': source_type
                })
        
        return json.dumps(results, indent=2, ensure_ascii=False)
    
    def verify_with_official_sources(claim: str) -> str:
        """Vérifie spécifiquement avec les sources officielles"""
        scraper = WebScraper()
        analyzer = TrustAnalyzer()
        
        # Recherche ciblée sur sources officielles
        official_results = []
        for domain in list(Config.TRUSTED_SOURCES.keys())[:5]:
            query = f"site:{domain} {claim}"
            urls = scraper.search_google(query, 2)
            
            for url in urls:
                data = scraper.scrape_url(url)
                if data['success']:
                    relevant_content = analyzer.extract_relevant_content(
                        data['content'], claim
                    )
                    if relevant_content:
                        official_results.append({
                            'domain': domain,
                            'url': url,
                            'relevant_content': relevant_content,
                            'trust_score': Config.TRUSTED_SOURCES[domain]['score']
                        })
        
        return json.dumps(official_results, indent=2, ensure_ascii=False)
    
    def analyze_credibility(sources_json: str) -> str:
        """Analyse la crédibilité globale basée sur les sources"""
        try:
            sources = json.loads(sources_json)
        except:
            sources = []
        
        if not sources:
            return "Aucune source disponible pour l'analyse"
        
        # Calcul du score de crédibilité pondéré
        total_score = 0
        total_weight = 0
        source_types = {}
        
        for source in sources:
            score = source.get('trust_score', 0)
            total_score += score
            total_weight += 1
            
            source_type = source.get('source_type', 'unknown')
            source_types[source_type] = source_types.get(source_type, 0) + 1
        
        avg_score = total_score / total_weight if total_weight > 0 else 0
        
        # Analyse
        analysis = {
            'average_trust_score': round(avg_score, 2),
            'num_sources': len(sources),
            'source_distribution': source_types,
            'credibility_level': 'HIGH' if avg_score > 0.7 else 'MEDIUM' if avg_score > 0.4 else 'LOW',
            'recommendation': 'Fiable' if avg_score > 0.7 else 'À vérifier' if avg_score > 0.4 else 'Peu fiable'
        }
        
        return json.dumps(analysis, indent=2, ensure_ascii=False)
    
    # Création des outils
    tools = [
        Tool(
            name="search_and_scrape",
            func=search_and_scrape,
            description="Recherche et extrait des informations du web sur un sujet donné"
        ),
        Tool(
            name="verify_official_sources",
            func=verify_with_official_sources,
            description="Vérifie une affirmation spécifiquement avec des sources officielles et institutionnelles"
        ),
        Tool(
            name="analyze_credibility",
            func=analyze_credibility,
            description="Analyse la crédibilité globale basée sur les sources trouvées"
        )
    ]
    
    return tools


# ============================================
# AGENT PRINCIPAL
# ============================================

class FactCheckerAgent:
    """Agent principal de vérification des faits"""
    
    def __init__(self):
        """Initialise l'agent avec LangChain"""
        
        # LLM
        self.llm = ChatOpenAI(
            model=Config.MODEL_NAME,
            temperature=0.1,  # Basse pour plus de précision
            openai_api_key=Config.OPENAI_API_KEY
        )
        
        # Outils
        self.tools = create_fact_checking_tools()
        
        # Prompt système
        self.system_prompt = """
        Tu es un expert en vérification des faits (fact-checker) rigoureux et méthodique.
        
        Ta mission est de :
        1. Vérifier la véracité des affirmations en utilisant des sources fiables
        2. Privilégier TOUJOURS les sources officielles et institutionnelles
        3. Fournir une analyse objective et nuancée
        4. Indiquer clairement le niveau de confiance de tes conclusions
        
        Méthodologie :
        1. D'ABORD chercher dans les sources officielles (gouvernement, ONU, OMS, etc.)
        2. ENSUITE élargir aux sources académiques et journalistiques réputées
        3. COMPARER les différentes sources et identifier les contradictions
        4. ÉVALUER la crédibilité globale
        5. CONCLURE avec un verdict clair et des recommandations
        
        Format de réponse attendu :
        - VERDICT : [VÉRIFIÉ / PARTIELLEMENT VÉRIFIÉ / NON VÉRIFIÉ / CONTRADICTOIRE]
        - CONFIANCE : [Score de 0 à 100%]
        - SOURCES OFFICIELLES : [Liste avec citations]
        - ANALYSE : [Explication détaillée]
        - RECOMMANDATIONS : [Actions suggérées]
        """
        
        # Prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Agent
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Memory
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=5  # Garde 5 derniers échanges
        )
        
        # Executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,  # Pour debug dans Cursor
            max_iterations=5,
            early_stopping_method="generate"
        )
    
    def verify_claim(self, claim: str, context: str = "") -> Dict[str, Any]:
        """
        Vérifie une affirmation
        
        Args:
            claim: L'affirmation à vérifier
            context: Contexte additionnel optionnel
            
        Returns:
            Dictionnaire avec le résultat de la vérification
        """
        
        # Construction de la requête
        query = f"""
        AFFIRMATION À VÉRIFIER :
        "{claim}"
        
        {f'CONTEXTE : {context}' if context else ''}
        
        Instructions :
        1. Recherche d'abord dans les sources officielles et gouvernementales
        2. Compare avec d'autres sources fiables
        3. Analyse la crédibilité globale
        4. Fournis un verdict clair avec justifications
        """
        
        try:
            # Exécution de l'agent
            result = self.agent_executor.run(query)
            
            # Post-traitement du résultat
            return self._parse_result(result, claim)
            
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e),
                "claim": claim,
                "message": "Une erreur est survenue lors de la vérification"
            }
    
    def _parse_result(self, raw_result: str, claim: str) -> Dict[str, Any]:
        """Parse et structure le résultat brut de l'agent"""
        
        # Extraction basique des éléments clés
        result = {
            "claim": claim,
            "raw_analysis": raw_result,
            "timestamp": datetime.now().isoformat(),
        }
        
        # Détection du verdict
        if "VÉRIFIÉ" in raw_result.upper() and "NON VÉRIFIÉ" not in raw_result.upper():
            if "PARTIELLEMENT" in raw_result.upper():
                result["verdict"] = VerificationStatus.PARTIALLY_VERIFIED.value
            else:
                result["verdict"] = VerificationStatus.VERIFIED.value
        elif "NON VÉRIFIÉ" in raw_result.upper():
            result["verdict"] = VerificationStatus.UNVERIFIED.value
        elif "CONTRADICTOIRE" in raw_result.upper():
            result["verdict"] = VerificationStatus.CONTRADICTORY.value
        else:
            result["verdict"] = VerificationStatus.INSUFFICIENT_DATA.value
        
        # Extraction du score de confiance (recherche de pourcentages)
        import re
        confidence_match = re.search(r'(\d+)%', raw_result)
        if confidence_match:
            result["confidence"] = int(confidence_match.group(1))
        else:
            result["confidence"] = 50  # Par défaut
        
        return result
    
    def batch_verify(self, claims: List[str]) -> List[Dict[str, Any]]:
        """Vérifie plusieurs affirmations en batch"""
        results = []
        for claim in claims:
            print(f"\n🔍 Vérification : {claim}")
            result = self.verify_claim(claim)
            results.append(result)
            print(f"✅ Verdict : {result.get('verdict', 'UNKNOWN')}")
        
        return results


# ============================================
# INTERFACE CURSOR AGENT MODE
# ============================================

class CursorAgentInterface:
    """Interface optimisée pour Cursor Agent Mode"""
    
    @staticmethod
    def run_interactive():
        """Mode interactif pour Cursor"""
        print("""
        ╔══════════════════════════════════════════════════════╗
        ║     🔍 FACT-CHECKER AGENT - Cursor Edition 🔍       ║
        ║                                                      ║
        ║  Vérification automatique avec sources officielles  ║
        ╚══════════════════════════════════════════════════════╝
        """)
        
        # Vérifier la clé API
        if Config.OPENAI_API_KEY == "your-key-here":
            print("⚠️  ATTENTION : Configure OPENAI_API_KEY dans le script ou .env")
            print("Pour continuer en mode démo, appuie sur Enter...")
            input()
        
        # Initialisation de l'agent
        print("\n🚀 Initialisation de l'agent...")
        agent = FactCheckerAgent()
        print("✅ Agent prêt !\n")
        
        # Boucle interactive
        while True:
            print("\n" + "="*50)
            print("Entre une affirmation à vérifier (ou 'quit' pour terminer) :")
            claim = input("📝 > ").strip()
            
            if claim.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Au revoir !")
                break
            
            if not claim:
                continue
            
            # Vérification
            print(f"\n🔍 Analyse en cours pour : '{claim}'")
            print("⏳ Recherche dans les sources officielles...")
            
            result = agent.verify_claim(claim)
            
            # Affichage du résultat
            print("\n" + "="*50)
            print("📊 RÉSULTAT DE LA VÉRIFICATION")
            print("="*50)
            
            print(f"\n📌 Affirmation : {result['claim']}")
            print(f"✅ Verdict : {result['verdict']}")
            print(f"📊 Confiance : {result.get('confidence', 'N/A')}%")
            print(f"\n📝 Analyse détaillée :")
            print("-"*50)
            
            # Affiche l'analyse en la formatant
            analysis = result.get('raw_analysis', 'Pas d\'analyse disponible')
            for line in analysis.split('\n'):
                if line.strip():
                    print(f"  {line.strip()}")
            
            print("\n" + "="*50)
    
    @staticmethod
    def run_batch_mode(claims_file: str = "claims.txt"):
        """Mode batch pour traiter plusieurs claims depuis un fichier"""
        
        print(f"\n📂 Lecture du fichier : {claims_file}")
        
        try:
            with open(claims_file, 'r', encoding='utf-8') as f:
                claims = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"❌ Fichier '{claims_file}' non trouvé !")
            print("Crée un fichier 'claims.txt' avec une affirmation par ligne.")
            return
        
        print(f"📋 {len(claims)} affirmations à vérifier\n")
        
        # Initialisation de l'agent
        agent = FactCheckerAgent()
        
        # Traitement batch
        results = agent.batch_verify(claims)
        
        # Sauvegarde des résultats
        output_file = f"verification_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Résultats sauvegardés dans : {output_file}")
        
        # Résumé
        print("\n📊 RÉSUMÉ :")
        print("-"*30)
        verified = sum(1 for r in results if "VÉRIFIÉ" in r.get('verdict', '') and "NON" not in r.get('verdict', ''))
        unverified = sum(1 for r in results if "NON VÉRIFIÉ" in r.get('verdict', ''))
        partial = sum(1 for r in results if "PARTIELLEMENT" in r.get('verdict', ''))
        
        print(f"✅ Vérifiés : {verified}")
        print(f"⚠️  Partiellement vérifiés : {partial}")
        print(f"❌ Non vérifiés : {unverified}")


# ============================================
# MAIN - POINT D'ENTRÉE CURSOR
# ============================================

def main():
    """
    Point d'entrée principal pour Cursor Agent Mode
    
    Usage dans Cursor :
    1. Ouvre ce fichier dans Cursor
    2. Active le mode Agent (Cmd+Shift+P -> "Toggle Agent Mode")
    3. Lance avec : python fact_checker_agent.py
    """
    
    import sys
    
    # Détection du mode
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "batch":
            # Mode batch
            file_path = sys.argv[2] if len(sys.argv) > 2 else "claims.txt"
            CursorAgentInterface.run_batch_mode(file_path)
        elif mode == "test":
            # Mode test avec exemples
            print("\n🧪 MODE TEST - Exemples de vérification\n")
            
            test_claims = [
                "La Tour Eiffel mesure 330 mètres de hauteur",
                "Emmanuel Macron est le président de la France en 2024",
                "Le vaccin COVID-19 contient des puces 5G",
                "L'eau bout à 100 degrés Celsius au niveau de la mer",
                "La Terre est plate"
            ]
            
            agent = FactCheckerAgent()
            
            for claim in test_claims:
                print(f"\n{'='*60}")
                print(f"TEST : {claim}")
                result = agent.verify_claim(claim)
                print(f"VERDICT : {result.get('verdict', 'UNKNOWN')}")
                print(f"CONFIANCE : {result.get('confidence', 'N/A')}%")
        else:
            print(f"❌ Mode inconnu : {mode}")
            print("Modes disponibles : interactive (défaut), batch, test")
    else:
        # Mode interactif par défaut
        CursorAgentInterface.run_interactive()


if __name__ == "__main__":
    main()
