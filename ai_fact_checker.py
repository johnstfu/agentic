# PATH: ai_fact_checker.py
"""
🤖 FACT-CHECKER IA HYBRIDE
Combine recherche réelle de sources + Analyse OpenAI intelligente
"""

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from duckduckgo_search import DDGS
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Sources de confiance (scoring)
TRUSTED_SOURCES = {
    "gouvernement.fr": 10, "service-public.fr": 10, "legifrance.gouv.fr": 10,
    "insee.fr": 10, "sante.gouv.fr": 10, "vaccination-info-service.fr": 10,
    "who.int": 9, "un.org": 9, "europa.eu": 9, "unesco.org": 9,
    "inserm.fr": 9, "pasteur.fr": 9, "pubmed.ncbi.nlm.nih.gov": 9,
    "nature.com": 8, "science.org": 8, "thelancet.com": 8, "cnrs.fr": 8,
    "snopes.com": 7, "factcheck.org": 7, "politifact.com": 7,
    "lemonde.fr/les-decodeurs": 7, "afp.com": 7, "francetvinfo.fr": 7,
    "lemonde.fr": 6, "ouest-france.fr": 6, "reuters.com": 6, "bbc.com": 6
}


class AIFactChecker:
    """Agent de fact-checking hybride : Recherche réelle + Analyse IA"""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def search_web(self, query: str, num_results: int = 10) -> list:
        """Recherche web multi-stratégies AMÉLIORÉE"""
        urls = []

        try:
            # Recherche 1 : Affirmation directe
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=num_results))
                urls.extend([r['href'] for r in results])

            # Recherche 2 : Fact-checkers FRANÇAIS (ciblés)
            factcheck_sites_fr = [
                "site:lemonde.fr/les-decodeurs",
                "site:liberation.fr/checknews",
                "site:factuel.afp.com",
                "site:francetvinfo.fr vrai-ou-faux"
            ]

            for site in factcheck_sites_fr:
                try:
                    with DDGS() as ddgs:
                        results = list(ddgs.text(f"{site} {query}", max_results=3))
                        urls.extend([r['href'] for r in results])
                except:
                    continue

            # Recherche 3 : Fact-checking international
            fact_query = f"{query} fact-check OR debunk OR vérification OR fake OR faux"
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(fact_query, max_results=5))
                    urls.extend([r['href'] for r in results])
            except:
                pass

            # Recherche 4 : Sites officiels
            official_sites = [
                "site:who.int",
                "site:gouvernement.fr",
                "site:inserm.fr",
                "site:pasteur.fr",
                "site:vaccination-info-service.fr"
            ]

            for domain in official_sites:
                try:
                    with DDGS() as ddgs:
                        results = list(ddgs.text(f"{domain} {query}", max_results=2))
                        urls.extend([r['href'] for r in results])
                except:
                    continue

            # Déduplication et limite
            unique_urls = list(dict.fromkeys(urls))
            return unique_urls[:20]  # Plus de sources potentielles

        except Exception as e:
            print(f"Erreur recherche: {e}")
            return []

    def extract_content(self, url: str) -> dict:
        """Extrait le contenu d'une URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Supprime scripts et styles
            for script in soup(["script", "style"]):
                script.decompose()

            title = soup.find('title').text if soup.find('title') else ''
            text = soup.get_text(separator=' ', strip=True)

            # Détection langue étrangère
            is_foreign = any(ord(char) > 0x3000 for char in text[:200])

            return {
                "url": url,
                "title": title,
                "content": text[:2000],  # 2000 premiers caractères
                "is_foreign": is_foreign,
                "success": True
            }
        except Exception as e:
            return {
                "url": url,
                "error": str(e),
                "success": False
            }

    def calculate_trust_score(self, url: str) -> tuple:
        """Calcule le score de confiance d'une URL"""
        domain = urlparse(url).netloc.lower()

        # Vérification dans sources connues
        for trusted_domain, score in TRUSTED_SOURCES.items():
            if trusted_domain in domain:
                return score / 10.0, self._get_source_type(score)

        # Domaines gouvernementaux
        if any(ext in domain for ext in ['.gouv.fr', '.gov', '.gouv.']):
            return 0.85, 'government'

        # Domaines académiques
        if any(ext in domain for ext in ['.edu', '.ac.uk', '.ac.be']):
            return 0.75, 'academic'

        # Médias régionaux français
        if any(media in domain for media in ['ouest-france', 'midilibre', 'sudouest']):
            return 0.55, 'news'

        # Organisations
        if '.org' in domain:
            return 0.45, 'organization'

        return 0.25, 'unknown'

    def _get_source_type(self, score: int) -> str:
        """Détermine le type de source selon le score"""
        if score >= 9:
            return 'institutional'
        elif score >= 7:
            return 'factcheck'
        elif score >= 6:
            return 'news'
        else:
            return 'other'

    def analyze_source_with_ai(self, claim: str, source_content: str, source_url: str) -> dict:
        """Utilise OpenAI pour analyser une source par rapport à l'affirmation"""

        prompt = f"""Tu es un expert en fact-checking. Analyse cette source par rapport à l'affirmation.

AFFIRMATION À VÉRIFIER :
"{claim}"

SOURCE ({source_url}) :
{source_content[:1500]}

INSTRUCTIONS :
1. La source parle-t-elle de cette affirmation ? (OUI/NON)
2. Si oui, la source CONFIRME-t-elle ou INFIRME-t-elle l'affirmation ?
3. Quelle est ta confiance dans cette évaluation ? (0-100%)
4. Résumé en 1-2 phrases de ce que dit la source

RÉPONDS AU FORMAT JSON STRICT :
{{
  "pertinence": "OUI" ou "NON",
  "position": "CONFIRME" ou "INFIRME" ou "NEUTRE",
  "confiance": 85,
  "resume": "La source explique que..."
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "Tu es un expert en fact-checking rigoureux. Réponds UNIQUEMENT en JSON valide."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=300
            )

            import json
            analysis = json.loads(response.choices[0].message.content.strip())
            return analysis

        except Exception as e:
            return {
                "pertinence": "NON",
                "position": "NEUTRE",
                "confiance": 0,
                "resume": f"Erreur d'analyse: {str(e)}"
            }

    def generate_final_verdict_with_ai(self, claim: str, sources_analysis: list) -> dict:
        """Génère le verdict final avec OpenAI basé sur toutes les sources"""

        # Prépare le résumé des sources
        sources_summary = []
        for src in sources_analysis:
            sources_summary.append(f"""
- {src['source_name']} ({src['trust_score']:.1f}/1.0) : {src['ai_analysis'].get('resume', 'N/A')}
  Position: {src['ai_analysis'].get('position', 'NEUTRE')}
""")

        prompt = f"""Tu es un expert fact-checker. Analyse toutes les sources et donne un VERDICT FINAL.

AFFIRMATION :
"{claim}"

SOURCES ANALYSÉES ({len(sources_analysis)}) :
{''.join(sources_summary[:10])}

INSTRUCTIONS :
1. Quel est le verdict global ? (VÉRIFIÉ / PARTIELLEMENT VÉRIFIÉ / NON VÉRIFIÉ / CONTRADICTOIRE)
2. Quel est ton niveau de confiance ? (0-100%)
3. Analyse détaillée en 3-5 phrases expliquant pourquoi

RÉPONDS AU FORMAT JSON STRICT :
{{
  "verdict": "VÉRIFIÉ" ou "NON VÉRIFIÉ" etc.,
  "confiance": 85,
  "analyse": "Explication détaillée..."
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "Tu es un fact-checker expert. Réponds en JSON valide."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500
            )

            import json
            verdict = json.loads(response.choices[0].message.content.strip())
            return verdict

        except Exception as e:
            return {
                "verdict": "ERREUR",
                "confiance": 0,
                "analyse": f"Impossible de générer le verdict: {str(e)}"
            }

    def verify_claim(self, claim: str, context: str = "") -> dict:
        """
        Vérification complète avec IA + LOGS TRANSPARENTS

        Pipeline:
        1. Recherche web (sources réelles)
        2. Extraction du contenu
        3. Filtrage (langue, pertinence)
        4. Analyse IA de chaque source
        5. Verdict final avec IA
        """

        logs = []  # Logs pour transparence
        logs.append(f"🔍 Démarrage analyse : '{claim}'")

        # 1. Recherche web
        logs.append("📡 Recherche web en cours...")
        urls = self.search_web(claim, 10)
        logs.append(f"✅ {len(urls)} URLs trouvées")

        if len(urls) == 0:
            logs.append("⚠️ AUCUNE URL trouvée - Vérification impossible")
            return {
                "claim": claim,
                "verdict": "❌ AUCUNE SOURCE TROUVÉE",
                "confidence": 0,
                "raw_analysis": "Impossible de trouver des sources sur le web. Vérifiez que l'affirmation est formulée clairement.",
                "sources": [],
                "stats": {
                    "total_sources": 0,
                    "sources_confirment": 0,
                    "sources_infirment": 0,
                    "sources_institutionnelles": 0
                },
                "logs": logs,
                "timestamp": datetime.now().isoformat()
            }

        # 2. Extraction et analyse
        sources_data = []
        logs.append(f"📄 Extraction et analyse de {min(len(urls), 12)} sources...")

        extraction_errors = 0
        filter_foreign = 0
        filter_pertinence = 0

        for idx, url in enumerate(urls[:12], 1):
            logs.append(f"  [{idx}] Analyse: {url[:60]}...")

            # Extraction contenu
            content_data = self.extract_content(url)

            if not content_data['success']:
                extraction_errors += 1
                logs.append(f"    ❌ Erreur extraction: {content_data.get('error', 'Inconnue')}")
                continue

            # Filtre langue étrangère (MOINS STRICT)
            if content_data.get('is_foreign', False):
                filter_foreign += 1
                logs.append(f"    ⚠️ Langue étrangère détectée - IGNORÉ")
                continue

            # Score de confiance
            trust_score, source_type = self.calculate_trust_score(url)
            logs.append(f"    📊 Score confiance: {trust_score:.2f} ({source_type})")

            # Analyse avec IA
            try:
                logs.append(f"    🤖 Analyse IA en cours...")
                ai_analysis = self.analyze_source_with_ai(
                    claim,
                    content_data['content'],
                    url
                )

                # Filtre pertinence (MOINS STRICT - garde NEUTRE aussi)
                if ai_analysis.get('pertinence') == 'NON':
                    filter_pertinence += 1
                    logs.append(f"    ⚠️ Source non pertinente - IGNORÉ")
                    continue

                logs.append(f"    ✅ Position: {ai_analysis.get('position')} (confiance IA: {ai_analysis.get('confiance')}%)")

            except Exception as e:
                logs.append(f"    ❌ Erreur analyse IA: {str(e)[:50]}")
                # On garde quand même la source même si IA fail
                ai_analysis = {
                    "pertinence": "OUI",
                    "position": "NEUTRE",
                    "confiance": 0,
                    "resume": f"Erreur analyse IA: {str(e)[:100]}"
                }

            source_info = {
                'url': url,
                'title': content_data['title'],
                'content': content_data['content'][:500],
                'trust_score': trust_score,
                'source_type': source_type,
                'source_name': self._get_source_name(url),
                'ai_analysis': ai_analysis
            }

            sources_data.append(source_info)
            logs.append(f"    ✓ Source ajoutée: {source_info['source_name']}")

        logs.append(f"\n📊 Résultat filtrage:")
        logs.append(f"  - Sources analysées: {len(sources_data)}")
        logs.append(f"  - Erreurs extraction: {extraction_errors}")
        logs.append(f"  - Filtrées (langue): {filter_foreign}")
        logs.append(f"  - Filtrées (pertinence): {filter_pertinence}")

        # 3. Verdict final avec IA
        if len(sources_data) == 0:
            logs.append("⚠️ AUCUNE source pertinente - Verdict par défaut")
            final_verdict = {
                "verdict": "❓ DONNÉES INSUFFISANTES",
                "confiance": 20,
                "analyse": f"Aucune source pertinente trouvée après analyse de {len(urls)} URLs. Filtrage: {extraction_errors} erreurs, {filter_foreign} langues étrangères, {filter_pertinence} non pertinentes."
            }
        else:
            logs.append(f"🤖 Génération verdict final avec {len(sources_data)} sources...")
            try:
                final_verdict = self.generate_final_verdict_with_ai(claim, sources_data)
                logs.append(f"✅ Verdict IA: {final_verdict.get('verdict')} (confiance: {final_verdict.get('confiance')}%)")
            except Exception as e:
                logs.append(f"❌ ERREUR génération verdict: {str(e)[:100]}")
                # Verdict de secours
                final_verdict = {
                    "verdict": "⚠️ ERREUR ANALYSE",
                    "confiance": 30,
                    "analyse": f"Erreur lors de la génération du verdict avec l'IA: {str(e)}"
                }

        # 4. Statistiques
        num_confirme = sum(1 for s in sources_data if s['ai_analysis'].get('position') == 'CONFIRME')
        num_infirme = sum(1 for s in sources_data if s['ai_analysis'].get('position') == 'INFIRME')
        num_institutional = sum(1 for s in sources_data if s['trust_score'] >= 0.8)

        logs.append(f"\n📈 Statistiques finales:")
        logs.append(f"  - Confirment: {num_confirme}")
        logs.append(f"  - Infirment: {num_infirme}")
        logs.append(f"  - Institutionnelles: {num_institutional}")

        return {
            "claim": claim,
            "verdict": final_verdict.get('verdict', 'INCONNU'),
            "confidence": final_verdict.get('confiance', 50),
            "raw_analysis": final_verdict.get('analyse', 'Aucune analyse'),
            "sources": sources_data,
            "stats": {
                "total_sources": len(sources_data),
                "sources_confirment": num_confirme,
                "sources_infirment": num_infirme,
                "sources_institutionnelles": num_institutional
            },
            "logs": logs,  # NOUVEAUTÉ : logs transparents
            "timestamp": datetime.now().isoformat()
        }

    def _get_source_name(self, url: str) -> str:
        """Extrait un nom lisible de la source"""
        domain = urlparse(url).netloc.lower()

        # Sources connues
        known_names = {
            "gouvernement.fr": "Gouvernement Français",
            "who.int": "OMS (WHO)",
            "inserm.fr": "INSERM",
            "pasteur.fr": "Institut Pasteur",
            "snopes.com": "Snopes",
            "factcheck.org": "FactCheck.org",
            "lemonde.fr": "Le Monde",
            "ouest-france.fr": "Ouest-France",
            "afp.com": "AFP",
            "reuters.com": "Reuters",
            "bbc.com": "BBC"
        }

        for key, name in known_names.items():
            if key in domain:
                return name

        # Extraction du domaine
        return domain.replace('www.', '').split('.')[0].title()
