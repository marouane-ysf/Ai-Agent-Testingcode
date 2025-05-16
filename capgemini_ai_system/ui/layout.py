"""
Gestion de la mise en page de l'application Streamlit.
"""

import streamlit as st
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from config.agents import AGENT_METADATA
from ui.components import render_header, render_agent_card, render_message, render_debug_info, render_download_buttons, render_context_info

def setup_page_config():
    """Configure les paramètres de la page Streamlit."""
    st.set_page_config(
        page_title="Capgemini AI Multi-Agent System",
        page_icon="☘️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Chargement du CSS
    st.markdown("""
    <style>
        .sub-header {
            font-size: 1.5rem;
            color: #003366;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        .progress-container {
            margin-top: 1rem;
        }
        .footer {
            text-align: center; 
            margin-top: 3rem; 
            color: #666; 
            font-size: 0.8rem;
        }
    </style>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Affiche la barre latérale de l'application."""
    with st.sidebar:
        # Logo Capgemini
        current_dir = Path(__file__).parent.parent
        image_path = os.path.join(current_dir, "assets", "capgemini-.png")
        
        try:
            st.image(image_path, width=190)
        except Exception:
            st.markdown("### Capgemini AI")
        
        # Sélection du mode d'orchestration
        mode = st.radio(
            "Choisissez un mode:",
            ["Orchestration Intelligente", "Séquence Multi-Agent", "Agent Unique"],
            index=0
        )
        
        if mode == "Orchestration Intelligente":
            st.session_state.orchestration_mode = "intelligent"
        elif mode == "Séquence Multi-Agent":
            st.session_state.orchestration_mode = "sequence"
        else:
            st.session_state.orchestration_mode = "single"
        
        # Interface pour définir la séquence personnalisée
        if st.session_state.orchestration_mode == "sequence":
            st.markdown("### Définir la séquence d'agents")
            sequence = []
            
            for agent_key in AGENT_METADATA:
                if agent_key != "router":
                    if st.checkbox(f"{AGENT_METADATA[agent_key]['icon']} {AGENT_METADATA[agent_key]['name']}", key=f"seq_{agent_key}"):
                        sequence.append(agent_key)
            
            # Permettre à l'utilisateur de définir l'ordre
            if sequence:
                sequence = st.multiselect(
                    "Définissez l'ordre des agents:",
                    options=sequence,
                    default=sequence,
                    key="agent_sequence_select"
                )
                st.session_state.agent_sequence = sequence
        
        # Si mode agent unique, sélecteur d'agent
        if st.session_state.orchestration_mode == "single":
            st.markdown("### Sélection d'agent")
            
            for agent_key in AGENT_METADATA:
                if agent_key != "router":
                    agent_info = AGENT_METADATA[agent_key]
                    if st.button(f"{agent_info['icon']} {agent_info['name']}", help=agent_info['description'], key=f"btn_{agent_key}"):
                        st.session_state.selected_agents = [agent_key]
        
        # Activation/désactivation du mode contexte
        st.session_state.context_mode = st.checkbox("Maintenir le contexte", value=True, 
                                                 help="Active/désactive la mémoire des conversations précédentes")
        
        # Mode debug
        st.session_state.debug_mode = st.checkbox("Mode debug", value=st.session_state.get("debug_mode", False))
        
        # Affichage des agents disponibles
        st.markdown("### Agents disponibles")
        
        for agent_key in AGENT_METADATA:
            if agent_key != "router" or st.session_state.orchestration_mode == "intelligent":
                selected = agent_key in st.session_state.get("selected_agents", [])
                render_agent_card(agent_key, selected)
        
        # Bouton de réinitialisation
        if st.button("🔄 Réinitialiser la conversation", help="Effacer l'historique de conversation"):
            st.session_state.messages = []
            st.session_state.current_results = None
            st.session_state.agent_sequence = []
            st.session_state.selected_agents = []
            st.session_state.processed_documents = []
            st.rerun()

def render_conversation():
    """Affiche la conversation en cours."""
    for message in st.session_state.get("messages", []):
        if message["role"] == "user":
            render_message("user", message["content"])
        else:
            agent_info = {
                "name": message.get("agent_name", "Assistant"),
                "icon": message.get("agent_icon", "🤖")
            } if "agent_name" in message else None
            
            render_message("assistant", message["content"], agent_info)
            
            # Affichage des informations de débogage si nécessaire
            if st.session_state.get("debug_mode", False) and "selection_method" in message:
                render_debug_info(message["selection_method"], message.get("router_response", "Non disponible"))

def render_progress():
    """Affiche la barre de progression."""
    if st.session_state.get("processing", False):
        st.markdown(f"<div class='progress-container'>{st.session_state.get('progress_text', 'Traitement en cours...')}</div>", unsafe_allow_html=True)
        st.progress(st.session_state.get("progress_value", 0))

def render_results():
    """Affiche les résultats et les options de téléchargement."""
    if not st.session_state.get("current_results"):
        return
    
    current_results = st.session_state.current_results
    
    if "error" in current_results:
        st.error(current_results["error"])
        return
    
    # Affichage des options de téléchargement si un document a été généré
    if "drafter" in current_results:
        render_download_buttons(current_results["drafter"])
    
    # Affichage des réponses détaillées par agent en mode expandable
    if all(agent in current_results for agent in ["quality", "drafter", "contracts_compare"]):
        with st.expander("📊 Voir les réponses détaillées de chaque agent"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### 🔍 Agent Qualité")
                st.markdown(current_results["quality"])
            
            with col2:
                st.markdown("#### 📝 Agent Rédacteur")
                st.markdown(current_results["drafter"])
            
            with col3:
                st.markdown("#### ⚖️ Agent Comparaison")
                st.markdown(current_results["contracts_compare"])

def render_context_debug():
    """Affiche les informations de contexte en mode debug."""
    if not st.session_state.get("debug_mode", False) or not st.session_state.get("context_mode", True):
        return
    
    from core.thread_manager import ThreadManager
    thread_manager = ThreadManager()
    threads_info = thread_manager.get_active_threads_info()
    
    if threads_info:
        render_context_info(threads_info)

def render_footer():
    """Affiche le pied de page."""
    st.markdown("""
    <div class="footer">
        <p>Développé pour Capgemini AI Agents - Système d'Orchestration Intelligente | 2025</p>
    </div>
    """, unsafe_allow_html=True)