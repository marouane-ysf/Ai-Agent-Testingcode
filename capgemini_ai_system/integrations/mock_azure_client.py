"""
Client simulé pour tester l'application sans connexion Azure.
"""

import asyncio
import uuid
from typing import List, Tuple, Dict, Any

class MockAzureClient:
    """Client simulé pour l'API Azure AI Foundry."""
    
    def __init__(self):
        """Initialise le client simulé."""
        self.threads = {}
    
    async def create_thread(self) -> str:
        """
        Crée un nouveau thread simulé.
        
        Returns:
            str: L'identifiant du thread créé
        """
        thread_id = str(uuid.uuid4())
        self.threads[thread_id] = []
        return thread_id
    
    async def get_thread(self, thread_id: str) -> bool:
        """
        Vérifie si un thread existe.
        
        Args:
            thread_id: L'identifiant du thread à vérifier
            
        Returns:
            bool: True si le thread existe, False sinon
        """
        return thread_id in self.threads
    
    async def add_message(self, thread_id: str, content: str) -> None:
        """
        Ajoute un message au thread.
        
        Args:
            thread_id: L'identifiant du thread
            content: Le contenu du message
        """
        if thread_id not in self.threads:
            self.threads[thread_id] = []
        self.threads[thread_id].append({"role": "user", "content": content})
    
    async def run_agent(self, thread_id: str, agent_key: str) -> str:
        """
        Simule l'exécution d'un agent.
        
        Args:
            thread_id: L'identifiant du thread
            agent_key: La clé de l'agent à exécuter
            
        Returns:
            str: La réponse simulée de l'agent
        """
        await asyncio.sleep(2)  # Simuler un délai
        
        query = self.threads[thread_id][-1]["content"] if self.threads[thread_id] else ""
        
        responses = {
            "quality": f"Analyse qualité de la requête: '{query[:30]}...'\n\nLa requête semble bien formulée et contient suffisamment d'informations pour être traitée efficacement.",
            "drafter": f"Ébauche basée sur: '{query[:30]}...'\n\n# Document préliminaire\n\nCeci est une ébauche générée automatiquement basée sur votre demande. Veuillez vérifier et ajuster selon vos besoins spécifiques.",
            "contracts_compare": f"Comparaison basée sur: '{query[:30]}...'\n\n## Tableau comparatif\n\n| Critère | Document A | Document B |\n|---------|------------|------------|\n| Durée   | 12 mois    | 24 mois    |\n| Prix    | Élevé      | Modéré     |",
            "market_comparison": "## Analyse de marché\n\nBasé sur l'analyse actuelle du marché, nous identifions trois principales options concurrentielles...",
            "negotiation": "### Stratégie de négociation\n\nPour optimiser votre position, nous recommandons d'adopter l'approche suivante...",
            "manager": "En tant que Manager Agent, je peux vous guider sur plusieurs aspects de cette requête...",
            "router": "quality, drafter"
        }
        
        response = responses.get(agent_key, f"Réponse simulée de l'agent {agent_key}")
        self.threads[thread_id].append({"role": "assistant", "content": response})
        
        return response
    
    async def router_analysis(self, query: str) -> Tuple[List[str], str]:
        """
        Simule l'analyse du Router Agent.
        
        Args:
            query: La requête à analyser
            
        Returns:
            Tuple[List[str], str]: Liste des agents sélectionnés et réponse brute
        """
        await asyncio.sleep(1)  # Simuler un délai
        
        if "qualité" in query.lower() or "analyser" in query.lower():
            return ["quality"], "quality"
        elif "rédiger" in query.lower() or "écrire" in query.lower():
            return ["drafter"], "drafter"
        elif "comparer" in query.lower():
            return ["contracts_compare"], "contracts_compare"
        elif "marché" in query.lower():
            return ["market_comparison"], "market_comparison"
        elif "négocier" in query.lower():
            return ["negotiation"], "negotiation"
        else:
            return ["quality", "drafter"], "quality, drafter"