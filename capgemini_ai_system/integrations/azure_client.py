"""
Client pour interagir avec les agents Azure AI Foundry.
"""
import os
import time
from azure.identity import DefaultAzureCredential
from semantic_kernel.agents import AzureAIAgent
from typing import Dict, List, Optional, Tuple, Any

from config.agents import AGENT_IDS
from config.settings import AZURE_AI_PROJECT_CONNECTION_STRING, AGENT_TIMEOUT

class AzureAIFoundryClient:
    """
    Client pour interagir avec les agents Azure AI Foundry.
    Gère les connexions, threads et exécutions des agents.
    """
    
    def __init__(self):
        """Initialise le client Azure AI Foundry."""
        self.project_conn_str = AZURE_AI_PROJECT_CONNECTION_STRING
        self.agent_client = None
        self.credential = None
        
    def __enter__(self):
        """Établit la connexion au service Azure AI."""
        print("Initialisation du client Azure AI...")
        self.credential = DefaultAzureCredential()
        self.agent_client = AzureAIAgent.create_client(credential=self.credential)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ferme proprement les connexions."""
        # Pas besoin de fermer le client explicitement
        pass
    
    def create_thread(self) -> str:
        """
        Crée un nouveau thread de conversation.
        
        Returns:
            str: L'identifiant du thread créé
        """
        if USE_MOCK:  # Ajoutez ces lignes
            return await self.mock_client.create_thread()
        thread = self.agent_client.agents.create_thread()
        return thread.id
    
    def get_thread(self, thread_id: str) -> bool:
        """
        Vérifie si un thread existe.
        
        Args:
            thread_id: L'identifiant du thread à vérifier
            
        Returns:
            bool: True si le thread existe, False sinon
        """
        try:
            self.agent_client.agents.get_thread(thread_id)
            return True
        except Exception:
            return False
    
    def add_message(self, thread_id: str, content: str) -> None:
        """
        Ajoute un message à un thread.
        
        Args:
            thread_id: L'identifiant du thread
            content: Le contenu du message
        """
        self.agent_client.agents.create_message(
            thread_id=thread_id,
            role="user",
            content=content
        )
    
    def run_agent(self, thread_id: str, agent_key: str) -> str:
        """
        Exécute un agent spécifique sur un thread.
        
        Args:
            thread_id: L'identifiant du thread
            agent_key: La clé de l'agent à exécuter
            
        Returns:
            str: La réponse de l'agent
            
        Raises:
            ValueError: Si l'agent spécifié n'existe pas
            RuntimeError: Si l'exécution échoue
        """
        if agent_key not in AGENT_IDS:
            raise ValueError(f"Agent '{agent_key}' non reconnu")
        
        agent_id = AGENT_IDS[agent_key]
        
        try:
            # Créer et démarrer l'exécution
            run = self.agent_client.agents.create_run(
                thread_id=thread_id,
                agent_id=agent_id
            )
            
            # Attendre la fin de l'exécution avec timeout
            start_time = time.time()
            while True:
                run = self.agent_client.agents.get_run(
                    thread_id=thread_id, 
                    run_id=run.id
                )
                if run.status == "completed":
                    break
                elif run.status in ["failed", "cancelled", "expired"]:
                    raise RuntimeError(f"Exécution terminée avec statut: {run.status}")
                
                # Vérifier le timeout
                if time.time() - start_time > AGENT_TIMEOUT:
                    raise TimeoutError(f"Timeout lors de l'exécution de l'agent {agent_key}")
                
                time.sleep(1)
            
            # Récupérer les messages
            messages = self.agent_client.agents.list_messages(thread_id=thread_id)
            assistant_messages = [m for m in messages.data if m.role == "assistant"]
            
            if not assistant_messages:
                return "Pas de réponse de l'agent"
            
            # Extraire le contenu de la dernière réponse
            latest_message = assistant_messages[-1]
            response = ""
            
            if latest_message.content:
                for content_item in latest_message.content:
                    if content_item.type == "text":
                        response += content_item.text.value
            
            return response
            
        except Exception as e:
            raise RuntimeError(f"Erreur lors de l'exécution de l'agent {agent_key}: {str(e)}")
    
    def router_analysis(self, query: str) -> Tuple[List[str], str]:
        """
        Utilise le Router Agent pour déterminer les agents appropriés.
        
        Args:
            query: La requête utilisateur à analyser
            
        Returns:
            Tuple[List[str], str]: Liste des agents sélectionnés et réponse brute
        """
        thread_id = self.create_thread()
        
        router_prompt = f"""
        Analyze this query and determine the most appropriate agents to handle it.
        Respond with a comma-separated list of agent names: quality, drafter, contracts_compare, market_comparison, negotiation, manager.

        Query: {query}

        Remember:
        - Choose "quality" for analysis, evaluation, or identification of issues
        - Choose "drafter" for writing, preparing documents, or creating templates
        - Choose "contracts_compare" for comparison of two or more contracts
        - Choose "market_comparison" for comparing market options and providing insights
        - Choose "negotiation" for assistance in negotiation strategies and tactics
        - Choose "manager" for general contract management questions

        Your comma-separated list of agents:
        """
        
        self.add_message(thread_id, router_prompt)
        
        raw_response = self.run_agent(thread_id, "router")
        selected_agents = [
            agent.strip() for agent in raw_response.split(",")
            if agent.strip() in AGENT_IDS
        ]
        
        return selected_agents, raw_response