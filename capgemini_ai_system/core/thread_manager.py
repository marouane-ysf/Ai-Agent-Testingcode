"""
Gestionnaire des threads de conversation pour les agents.
"""

import streamlit as st
from typing import Dict, Optional, List, Any
import datetime

from integrations.azure_client import AzureAIFoundryClient
from config.agents import AGENT_IDS, AGENT_METADATA

class ThreadManager:
    """
    Gère les threads de conversation pour les agents.
    Maintient le contexte des conversations précédentes.
    """
    
    def __init__(self):
        """Initialise le gestionnaire de threads."""
        self.client = None
        
        # Initialiser les variables de session si nécessaires
        if 'agent_threads' not in st.session_state:
            st.session_state.agent_threads = {}
        if 'thread_history' not in st.session_state:
            st.session_state.thread_history = {}
        if 'thread_timestamps' not in st.session_state:
            st.session_state.thread_timestamps = {}
    
    async def _get_client(self) -> AzureAIFoundryClient:
        """
        Obtient une instance du client Azure AI Foundry.
        
        Returns:
            AzureAIFoundryClient: Une instance du client
        """
        if self.client is None:
            self.client = AzureAIFoundryClient()
        return self.client
    
    async def get_thread_for_agent(self, agent_key: str, create_if_missing: bool = True) -> Optional[str]:
        """
        Obtient l'ID du thread associé à un agent.
        Crée un nouveau thread si nécessaire et si autorisé.
        
        Args:
            agent_key: La clé de l'agent
            create_if_missing: Indique s'il faut créer un thread si aucun n'existe
            
        Returns:
            Optional[str]: L'ID du thread, ou None si aucun thread n'existe et create_if_missing est False
        """
        # Vérifier si un thread existe déjà pour cet agent
        if agent_key in st.session_state.agent_threads:
            thread_id = st.session_state.agent_threads[agent_key]
            
            # Vérifier si le thread existe toujours dans Azure
            client = await self._get_client()
            thread_exists = await client.get_thread(thread_id)
            
            if thread_exists:
                # Mettre à jour le timestamp
                st.session_state.thread_timestamps[agent_key] = datetime.datetime.now()
                return thread_id
        
        # Créer un nouveau thread si nécessaire
        if create_if_missing:
            client = await self._get_client()
            thread_id = await client.create_thread()
            
            st.session_state.agent_threads[agent_key] = thread_id
            st.session_state.thread_timestamps[agent_key] = datetime.datetime.now()
            st.session_state.thread_history[agent_key] = []
            
            return thread_id
        
        return None
    
    def reset_thread(self, agent_key: str) -> None:
        """
        Réinitialise le thread pour un agent spécifique.
        
        Args:
            agent_key: La clé de l'agent
        """
        if agent_key in st.session_state.agent_threads:
            del st.session_state.agent_threads[agent_key]
        if agent_key in st.session_state.thread_history:
            del st.session_state.thread_history[agent_key]
        if agent_key in st.session_state.thread_timestamps:
            del st.session_state.thread_timestamps[agent_key]
    
    def reset_all_threads(self) -> None:
        """Réinitialise tous les threads de conversation."""
        st.session_state.agent_threads = {}
        st.session_state.thread_history = {}
        st.session_state.thread_timestamps = {}
    
    def add_to_history(self, agent_key: str, role: str, content: str) -> None:
        """
        Ajoute un message à l'historique du thread d'un agent.
        
        Args:
            agent_key: La clé de l'agent
            role: Le rôle du message ('user' ou 'assistant')
            content: Le contenu du message
        """
        if agent_key not in st.session_state.thread_history:
            st.session_state.thread_history[agent_key] = []
        
        st.session_state.thread_history[agent_key].append({
            'role': role,
            'content': content,
            'timestamp': datetime.datetime.now()
        })
        
        # Limiter la taille de l'historique (garder les 10 derniers messages)
        if len(st.session_state.thread_history[agent_key]) > 10:
            st.session_state.thread_history[agent_key] = st.session_state.thread_history[agent_key][-10:]
    
    def get_history(self, agent_key: str, max_messages: int = 5) -> List[Dict]:
        """
        Récupère l'historique des messages pour un agent.
        
        Args:
            agent_key: La clé de l'agent
            max_messages: Nombre maximum de messages à récupérer
            
        Returns:
            List[Dict]: Liste des messages d'historique
        """
        if agent_key not in st.session_state.thread_history:
            return []
        
        # Retourner les n derniers messages
        return st.session_state.thread_history[agent_key][-max_messages:]
    
    def format_history_as_context(self, agent_key: str, max_messages: int = 3) -> str:
        """
        Formate l'historique des messages comme contexte pour un agent.
        
        Args:
            agent_key: La clé de l'agent
            max_messages: Nombre maximum de messages à inclure
            
        Returns:
            str: Contexte formaté pour l'agent
        """
        history = self.get_history(agent_key, max_messages)
        
        if not history:
            return ""
        
        context = "Contexte des échanges précédents :\n\n"
        for msg in history:
            role_name = "Utilisateur" if msg['role'] == 'user' else f"Agent {AGENT_METADATA.get(agent_key, {}).get('name', 'Assistant')}"
            context += f"{role_name}: {msg['content']}\n\n"
        
        return context
    
    def is_context_enabled(self) -> bool:
        """
        Vérifie si le mode contexte est activé.
        
        Returns:
            bool: True si le mode contexte est activé, False sinon
        """
        return st.session_state.get('context_mode', True)
    
    def get_active_threads_info(self) -> List[Dict]:
        """
        Récupère les informations sur les threads actifs.
        Utile pour le debugging.
        
        Returns:
            List[Dict]: Informations sur les threads actifs
        """
        info = []
        
        for agent_key, thread_id in st.session_state.agent_threads.items():
            last_activity = st.session_state.thread_timestamps.get(agent_key, datetime.datetime.min)
            messages_count = len(st.session_state.thread_history.get(agent_key, []))
            
            info.append({
                'agent': agent_key,
                'agent_name': AGENT_METADATA.get(agent_key, {}).get('name', 'Inconnu'),
                'thread_id': thread_id,
                'last_activity': last_activity,
                'messages_count': messages_count
            })
        
        # Trier par activité récente
        info.sort(key=lambda x: x['last_activity'], reverse=True)
        
        return info