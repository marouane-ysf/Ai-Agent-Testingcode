"""
Gestion de l'état de session Streamlit.
"""

import streamlit as st
from typing import Dict, List, Any, Optional

def initialize_session_state():
    """Initialise les variables d'état de session nécessaires."""
    # Variables pour les messages et résultats
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_results" not in st.session_state:
        st.session_state.current_results = None
    
    # Variables pour le traitement et la progression
    if "processing" not in st.session_state:
        st.session_state.processing = False
    if "progress_text" not in st.session_state:
        st.session_state.progress_text = ""
    if "progress_value" not in st.session_state:
        st.session_state.progress_value = 0
    
    # Variables pour la configuration
    if "orchestration_mode" not in st.session_state:
        st.session_state.orchestration_mode = "intelligent"
    if "selected_agents" not in st.session_state:
        st.session_state.selected_agents = []
    if "agent_sequence" not in st.session_state:
        st.session_state.agent_sequence = []
    
    # Variables pour les fonctionnalités
    if "context_mode" not in st.session_state:
        st.session_state.context_mode = True
    if "debug_mode" not in st.session_state:
        st.session_state.debug_mode = False
    
    # Variables pour les documents
    if "processed_documents" not in st.session_state:
        st.session_state.processed_documents = []

def add_message(role: str, content: str, **kwargs):
    """
    Ajoute un message à l'historique de conversation.
    
    Args:
        role: Rôle du message ('user' ou 'assistant')
        content: Contenu du message
        **kwargs: Attributs supplémentaires à stocker avec le message
    """
    message = {
        "role": role,
        "content": content,
        **kwargs
    }
    
    st.session_state.messages.append(message)

def set_processing(state: bool, text: str = "", value: float = 0):
    """
    Définit l'état de traitement et met à jour la barre de progression.
    
    Args:
        state: État de traitement (True/False)
        text: Texte descriptif
        value: Valeur de progression (0-1)
    """
    st.session_state.processing = state
    
    if state:
        st.session_state.progress_text = text
        st.session_state.progress_value = value
    else:
        st.session_state.progress_text = ""
        st.session_state.progress_value = 0

def get_current_mode() -> tuple:
    """
    Récupère le mode actuel et les informations associées.
    
    Returns:
        tuple: (mode, sequence/agent)
    """
    mode = st.session_state.orchestration_mode
    
    if mode == "intelligent":
        return mode, None
    elif mode == "sequence":
        return mode, st.session_state.get("agent_sequence", [])
    elif mode == "single":
        return mode, st.session_state.get("selected_agents", [])[0] if st.session_state.get("selected_agents") else None
    
    return "intelligent", None

def clear_session():
    """Efface la session et réinitialise toutes les variables d'état."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    initialize_session_state()