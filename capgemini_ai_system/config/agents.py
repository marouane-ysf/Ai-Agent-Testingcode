"""
Configuration des agents Azure AI Foundry.
Ce fichier contient les identifiants et métadonnées des agents.
"""

import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Identifiants des agents
AGENT_IDS = {
    "manager": os.environ.get("MANAGER_AGENT_ID"),
    "quality": os.environ.get("QUALITY_AGENT_ID"),
    "drafter": os.environ.get("DRAFT_AGENT_ID"),
    "contracts_compare": os.environ.get("COMPARE_AGENT_ID"),
    "router": os.environ.get("ROUTER_AGENT_ID"),
    "market_comparison": os.environ.get("MarketComparisonAgent_ID"),
    "negotiation": os.environ.get("NegotiationAgent_ID")
}

# Métadonnées des agents pour l'interface utilisateur
AGENT_METADATA = {
    "router": {
        "name": "Router Agent", 
        "icon": "🧭", 
        "description": "Détermine les agents les plus appropriés pour chaque requête"
    },
    "manager": {
        "name": "Manager Agent", 
        "icon": "🧭", 
        "description": "Répond aux questions générales sur le management de contrat"
    },
    "quality": {
        "name": "Agent Qualité", 
        "icon": "🔍", 
        "description": "Évalue la qualité des contrats et identifie les erreurs clés"
    },
    "drafter": {
        "name": "Agent Rédacteur", 
        "icon": "📝", 
        "description": "Prépare des ébauches structurées de contrats et documents"
    },
    "contracts_compare": {
        "name": "Agent Comparaison de Contrats", 
        "icon": "⚖️", 
        "description": "Compare les contrats et fournit un tableau de comparaison"
    },
    "market_comparison": {
        "name": "Agent Comparaison de Marché", 
        "icon": "📊", 
        "description": "Compare différentes options de marché et fournit des insights"
    },
    "negotiation": {
        "name": "Agent Négociation", 
        "icon": "🤝", 
        "description": "Assiste dans les stratégies et tactiques de négociation"
    }
}

# Mots-clés pour la détection heuristique des agents
AGENT_KEYWORDS = {
    "quality": ['analys', 'évalue', 'qualité', 'risque', 'examine', 'erreur', 'faiblesse', 
                'problème', 'conformité', 'lacune', 'vérifi', 'identifi'],
    "drafter": ['rédige', 'rédaction', 'écri', 'ébauche', 'contrat', 'prépar', 'modèle', 
                'template', 'document', 'structure', 'clause', 'formulaire'],
    "contracts_compare": ['compar', 'contrat', 'analyse', 'différence', 'similitude', 
                          'contraste', 'évaluation', 'examen', 'point de comparaison'],
    "market_comparison": ['compar', 'marché', 'option', 'insight', 'benchmark'],
    "negotiation": ['négoci', 'stratégie', 'tactique', 'accord', 'contrat', 'discussion']
}

# Expressions régulières pour la détection d'intentions
AGENT_PATTERNS = {
    "drafter": r'(rédige[rz]?|écri[rstvez]+|prépar[ez]+)\s+([uneod]+\s+)?(ébauche|contrat|document|proposition)',
    "quality": r'(analyse[rz]?|évalue[rz]?|identifi[ez]+|vérifi[ez]+)\s+([uncedo]+\s+)?(contrat|document|qualité|risque)',
    "contracts_compare": r'(compar[eai]+\s+)?(contrat|document|analyse|différence|similitude|contraste)',
    "market_comparison": r'(compar[eai]+\s+)?(marché|option|insight|analyse de marché|benchmark)',
    "negotiation": r'(négoci[eai]+\s+)?(stratégie|tactique|accord|contrat|discussion|proposition)'
}

# Groupes d'agents par catégorie (pour le fallback)
AGENT_CATEGORIES = {
    "analyse": ["quality", "contracts_compare"],
    "rédaction": ["drafter"],
    "comparaison": ["contracts_compare", "market_comparison"],
    "négociation": ["negotiation"],
    "conseil": ["manager"]
}