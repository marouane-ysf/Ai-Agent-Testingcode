"""
Gestionnaire pour l'exécution et la coordination des agents.
"""

import re
import asyncio
from typing import List, Dict, Any, Tuple, Optional

from integrations.azure_client import AzureAIFoundryClient
from config.agents import AGENT_IDS, AGENT_METADATA, AGENT_KEYWORDS, AGENT_PATTERNS

class AgentManager:
    """
    Gère la sélection et l'exécution des agents.
    """
    
    def __init__(self):
        """Initialise le gestionnaire d'agents."""
        self.client = None
        self.last_router_response = None
    
    async def _get_client(self) -> AzureAIFoundryClient:
        """
        Obtient une instance du client Azure AI Foundry.
        
        Returns:
            AzureAIFoundryClient: Une instance du client
        """
        if self.client is None:
            self.client = AzureAIFoundryClient()
        return self.client
    
    async def execute_agent(self, agent_key: str, query: str) -> str:
        """
        Exécute un agent spécifique.
        
        Args:
            agent_key: La clé de l'agent à exécuter
            query: La requête à soumettre à l'agent
            
        Returns:
            str: La réponse de l'agent
        """
        client = await self._get_client()
        
        # Créer un nouveau thread pour l'agent
        thread_id = await client.create_thread()
        
        # Ajouter le message au thread
        await client.add_message(thread_id, query)
        
        # Exécuter l'agent
        response = await client.run_agent(thread_id, agent_key)
        
        return response
    
    def _heuristic_agent_selection(self, query: str) -> Tuple[List[str], str]:
        """
        Utilise des heuristiques pour déterminer les agents appropriés.
        
        Args:
            query: La requête utilisateur
            
        Returns:
            Tuple[List[str], str]: Liste des agents sélectionnés et méthode de sélection
        """
        query = query.lower()
        
        # Vérifier les patterns d'intention
        for agent, pattern in AGENT_PATTERNS.items():
            if re.search(pattern, query):
                return [agent], f"Pattern détecté: {pattern}"
        
        # Compter les occurrences de mots-clés
        keyword_counts = {agent: 0 for agent in AGENT_KEYWORDS}
        for agent, keywords in AGENT_KEYWORDS.items():
            keyword_counts[agent] = sum(1 for keyword in keywords if keyword in query)
        
        # Sélectionner les agents avec des occurrences de mots-clés
        selected_agents = [agent for agent, count in keyword_counts.items() if count > 0]
        
        # Si aucun agent n'a été sélectionné, utiliser des heuristiques plus générales
        if not selected_agents:
            if any(word in query for word in ['créer', 'faire', 'rédiger', 'écrire', 'préparer']):
                return ["drafter"], "Intention de création détectée"
            elif any(word in query for word in ['analyser', 'évaluer', 'vérifier', 'examiner']):
                return ["quality"], "Intention d'analyse détectée"
            else:
                return ["quality"], "Fallback par défaut: Agent Qualité"
        
        return selected_agents, "Basé sur les occurrences de mots-clés"
    
    async def determine_agents(self, query: str) -> Tuple[List[str], str, str]:
        """
        Détermine les agents les plus appropriés pour une requête.
        
        Args:
            query: La requête utilisateur
            
        Returns:
            Tuple[List[str], str, str]: Liste des agents, méthode de sélection, réponse brute du router
        """
        # D'abord, essayer avec le Router Agent
        try:
            client = await self._get_client()
            selected_agents, raw_response = await client.router_analysis(query)
            
            self.last_router_response = raw_response
            
            # Vérifier que les agents retournés sont valides
            valid_agents = [agent for agent in selected_agents if agent in AGENT_IDS]
            
            if valid_agents:
                return valid_agents, "Router Agent", raw_response
            
        except Exception as e:
            print(f"Erreur lors de l'utilisation du Router Agent: {str(e)}")
        
        # Fallback sur la sélection heuristique
        heuristic_agents, reason = self._heuristic_agent_selection(query)
        return heuristic_agents, f"Heuristique ({reason})", "Erreur du Router Agent - Fallback heuristique"
    
    async def execute_quality_analysis(self, query: str) -> Optional[str]:
        """
        Effectue une analyse préliminaire avec l'Agent Qualité.
        
        Args:
            query: La requête utilisateur
            
        Returns:
            Optional[str]: Résultat de l'analyse qualité, ou None en cas d'erreur
        """
        try:
            prompt = f"Faites une analyse rapide et concise de cette requête: {query}"
            analysis = await self.execute_agent("quality", prompt)
            return analysis
        except Exception as e:
            print(f"Erreur lors de l'analyse préliminaire de qualité: {str(e)}")
            return None
    
    async def execute_agents_in_sequence(self, query: str, agent_sequence: List[str]) -> Dict[str, str]:
        """
        Exécute une séquence d'agents, chacun prenant en compte la réponse du précédent.
        
        Args:
            query: La requête initiale
            agent_sequence: La séquence d'agents à exécuter
            
        Returns:
            Dict[str, str]: Réponses de chaque agent
        """
        responses = {}
        current_context = query
        
        for agent in agent_sequence:
            response = await self.execute_agent(agent, current_context)
            responses[agent] = response
            
            # Mettre à jour le contexte pour l'agent suivant
            current_context = f"Tenant compte de cette réponse: {response}\n\nQuestion initiale: {query}"
        
        return responses
    
    async def execute_agents_in_parallel(self, query: str, agents: List[str]) -> Dict[str, str]:
        """
        Exécute plusieurs agents en parallèle.
        
        Args:
            query: La requête utilisateur
            agents: Liste des agents à exécuter
            
        Returns:
            Dict[str, str]: Réponses de chaque agent
        """
        tasks = {agent: self.execute_agent(agent, query) for agent in agents}
        
        # Attendre que toutes les tâches soient terminées
        responses = {}
        for agent, task in tasks.items():
            try:
                responses[agent] = await task
            except Exception as e:
                responses[agent] = f"Erreur d'exécution: {str(e)}"
        
        return responses