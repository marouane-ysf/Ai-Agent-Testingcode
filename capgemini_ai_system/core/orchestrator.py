"""
Orchestrateur principal pour coordonner les flux de travail.
"""

import asyncio
from typing import Dict, List, Optional, Any
import streamlit as st

from core.agent_manager import AgentManager
from core.thread_manager import ThreadManager
from core.document_processor import DocumentProcessor
from config.agents import AGENT_METADATA
from utils.async_helpers import run_async

class Orchestrator:
    """
    Coordonne l'exécution des différents workflows et composants.
    """
    
    def __init__(self):
        """Initialise les services nécessaires."""
        self.agent_manager = AgentManager()
        self.thread_manager = ThreadManager()
        self.document_processor = DocumentProcessor()
    
    def update_progress(self, text: str, value: float) -> None:
        """
        Met à jour la barre de progression dans l'interface.
        
        Args:
            text: Texte descriptif
            value: Valeur de progression (0-1)
        """
        st.session_state.progress_text = text
        st.session_state.progress_value = value
        
    async def orchestrate_intelligent_workflow(
        self, 
        query: str, 
        files: Optional[List[Any]] = None,
        ocr_enabled: bool = False
    ) -> Dict[str, Any]:
        """
        Exécute le workflow d'orchestration intelligente.
        
        Args:
            query: Requête utilisateur
            files: Liste des fichiers uploadés
            ocr_enabled: Indique si l'OCR est activé
            
        Returns:
            Dict[str, Any]: Résultat d'orchestration avec réponses des agents
        """
        try:
            # Traitement des documents
            if files:
                self.update_progress("Traitement des documents...", 0.1)
                processed_query = await self.document_processor.process_documents(query, files, ocr_enabled)
            else:
                processed_query = query
                
            # Détermination des agents appropriés
            self.update_progress("Analyse de votre requête...", 0.2)
            selected_agents, selection_method, router_response = await self.agent_manager.determine_agents(processed_query)
            
            if not selected_agents:
                return {
                    "error": "Aucun agent approprié n'a pu être identifié pour cette requête."
                }
                
            self.update_progress(
                f"Agents sélectionnés: {', '.join(AGENT_METADATA[agent]['name'] for agent in selected_agents)}", 
                0.3
            )
            
            # Exécution préliminaire de l'agent Qualité si nécessaire
            context = None
            if "quality" not in selected_agents:
                self.update_progress("Analyse préliminaire de qualité...", 0.4)
                context = await self.agent_manager.execute_quality_analysis(processed_query)
            
            # Exécution des agents sélectionnés
            responses = {}
            for i, agent in enumerate(selected_agents):
                progress = 0.5 + (i / len(selected_agents) * 0.4)
                self.update_progress(
                    f"{AGENT_METADATA[agent]['icon']} {AGENT_METADATA[agent]['name']}: Traitement...", 
                    progress
                )
                
                agent_query = processed_query
                if context:
                    agent_query = f"En tenant compte de cette analyse: {context}\n\n{processed_query}"
                
                response = await self.agent_manager.execute_agent(agent, agent_query)
                responses[agent] = response
                
                # Sauvegarder dans l'historique si le mode contexte est activé
                if self.thread_manager.is_context_enabled():
                    self.thread_manager.add_to_history(agent, 'user', processed_query)
                    self.thread_manager.add_to_history(agent, 'assistant', response)
            
            # Combinaison des réponses
            self.update_progress("Finalisation des résultats...", 0.9)
            combined_response = ""
            for agent in selected_agents:
                combined_response += f"{AGENT_METADATA[agent]['name']}:\n{responses[agent]}\n\n"
            
            # Formatage du résultat final
            self.update_progress("Traitement terminé", 1.0)
            result = {
                "selected_agents": selected_agents,
                "agent_names": [AGENT_METADATA[agent]['name'] for agent in selected_agents],
                "agent_icons": [AGENT_METADATA[agent]['icon'] for agent in selected_agents],
                "combined": combined_response,
                "selection_method": selection_method,
                "router_response": router_response,
                **responses
            }
            
            return result
            
        except Exception as e:
            return {"error": f"Erreur d'orchestration: {str(e)}"}
    
    async def orchestrate_sequential_workflow(
        self, 
        query: str, 
        sequence: List[str],
        files: Optional[List[Any]] = None,
        ocr_enabled: bool = False
    ) -> Dict[str, Any]:
        """
        Exécute un workflow séquentiel avec les agents spécifiés.
        
        Args:
            query: Requête utilisateur
            sequence: Séquence d'agents à exécuter
            files: Liste des fichiers uploadés
            ocr_enabled: Indique si l'OCR est activé
            
        Returns:
            Dict[str, Any]: Résultat d'orchestration avec réponses des agents
        """
        try:
            # Validation de la séquence
            if not sequence:
                return {"error": "Séquence d'agents vide."}
                
            for agent in sequence:
                if agent not in AGENT_METADATA:
                    return {"error": f"Agent inconnu dans la séquence: {agent}"}
            
            # Traitement des documents
            if files:
                self.update_progress("Traitement des documents...", 0.1)
                processed_query = await self.document_processor.process_documents(query, files, ocr_enabled)
            else:
                processed_query = query
            
            # Exécution séquentielle
            responses = await self.agent_manager.execute_agents_in_sequence(processed_query, sequence)
            
            # Combinaison des réponses
            combined_response = ""
            for agent in sequence:
                combined_response += f"{AGENT_METADATA[agent]['name']}:\n{responses[agent]}\n\n"
            
            self.update_progress("Traitement terminé", 1.0)
            return {
                "selected_agents": sequence,
                "agent_names": [AGENT_METADATA[agent]['name'] for agent in sequence],
                "agent_icons": [AGENT_METADATA[agent]['icon'] for agent in sequence],
                "combined": combined_response,
                **responses
            }
            
        except Exception as e:
            return {"error": f"Erreur d'orchestration séquentielle: {str(e)}"}
    
    async def orchestrate_single_agent(
        self, 
        query: str, 
        agent: str,
        files: Optional[List[Any]] = None,
        ocr_enabled: bool = False
    ) -> Dict[str, Any]:
        """
        Exécute un workflow avec un agent unique.
        
        Args:
            query: Requête utilisateur
            agent: Agent à utiliser
            files: Liste des fichiers uploadés
            ocr_enabled: Indique si l'OCR est activé
            
        Returns:
            Dict[str, Any]: Résultat d'orchestration avec réponse de l'agent
        """
        try:
            # Validation de l'agent
            if agent not in AGENT_METADATA:
                return {"error": f"Agent inconnu: {agent}"}
            
            # Traitement des documents
            if files:
                self.update_progress("Traitement des documents...", 0.1)
                processed_query = await self.document_processor.process_documents(query, files, ocr_enabled)
            else:
                processed_query = query
            
            # Exécution de l'agent
            self.update_progress(
                f"{AGENT_METADATA[agent]['icon']} {AGENT_METADATA[agent]['name']}: Traitement...", 
                0.5
            )
            
            # Récupérer l'historique si le mode contexte est activé
            if self.thread_manager.is_context_enabled():
                context = self.thread_manager.format_history_as_context(agent)
                if context:
                    processed_query = f"{context}\n\nNouvelle requête: {processed_query}"
            
            response = await self.agent_manager.execute_agent(agent, processed_query)
            
            # Sauvegarder dans l'historique si le mode contexte est activé
            if self.thread_manager.is_context_enabled():
                self.thread_manager.add_to_history(agent, 'user', query)
                self.thread_manager.add_to_history(agent, 'assistant', response)
            
            self.update_progress("Traitement terminé", 1.0)
            return {
                "selected_agent": agent,
                "agent_name": AGENT_METADATA[agent]['name'],
                "agent_icon": AGENT_METADATA[agent]['icon'],
                "combined": response,
                agent: response
            }
            
        except Exception as e:
            return {"error": f"Erreur d'exécution de l'agent {agent}: {str(e)}"}
    
    def orchestrate(
        self, 
        query: str, 
        mode: str = "intelligent",
        agent_sequence: Optional[List[str]] = None,
        single_agent: Optional[str] = None,
        files: Optional[List[Any]] = None,
        ocr_enabled: bool = False
    ) -> Dict[str, Any]:
        """
        Point d'entrée principal pour l'orchestration basée sur le mode.
        
        Args:
            query: Requête utilisateur
            mode: Mode d'orchestration ('intelligent', 'sequence', 'single')
            agent_sequence: Séquence d'agents pour le mode 'sequence'
            single_agent: Agent unique pour le mode 'single'
            files: Liste des fichiers uploadés
            ocr_enabled: Indique si l'OCR est activé
            
        Returns:
            Dict[str, Any]: Résultat d'orchestration
        """
        if mode == "intelligent":
            return run_async(self.orchestrate_intelligent_workflow(query, files, ocr_enabled))
        elif mode == "sequence":
            if not agent_sequence:
                return {"error": "Séquence d'agents non spécifiée pour le mode séquentiel."}
            return run_async(self.orchestrate_sequential_workflow(query, agent_sequence, files, ocr_enabled))
        elif mode == "single":
            if not single_agent:
                return {"error": "Agent non spécifié pour le mode agent unique."}
            return run_async(self.orchestrate_single_agent(query, single_agent, files, ocr_enabled))
        else:
            return {"error": f"Mode d'orchestration non reconnu: {mode}"}