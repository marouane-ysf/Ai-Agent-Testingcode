"""
Application principale Capgemini AI Multi-Agent System.
Point d'entrée de l'application Streamlit.
"""

import streamlit as st
from pathlib import Path
import os
from typing import Dict, List, Any, Optional

# Import des composants de l'application
from ui.state import initialize_session_state, add_message, set_processing, get_current_mode, clear_session
from ui.layout import setup_page_config, render_sidebar, render_header, render_conversation, render_progress, render_results, render_context_debug, render_footer
from core.orchestrator import Orchestrator
from utils.text_extraction import extract_text_from_multiple_files

def main():
    """Fonction principale de l'application."""
    # Initialisation de l'état de session
    initialize_session_state()
    
    # Configuration de la page
    setup_page_config()
    
    # Affichage de l'en-tête
    render_header()
    
    # Affichage de la barre latérale
    render_sidebar()
    
    # Conteneur principal
    main_container = st.container()
    
    with main_container:
        # Affichage de la conversation
        render_conversation()
        
        # Affichage de la barre de progression
        render_progress()
        
        # Affichage des résultats actuels
        render_results()
        
        # Affichage des informations de débogage du contexte
        render_context_debug()
        
        # Checkbox pour activer l'OCR
        ocr_enabled = st.checkbox("Activer l'OCR pour les PDF scannés", key="ocr_enabled")
        
        # Zone de saisie utilisateur
        user_input = st.chat_input(
            "Tapez votre message ici...", 
            disabled=st.session_state.processing,
            accept_file="multiple"
        )
        
        # Traitement de l'entrée utilisateur
        if user_input:
            user_text = user_input["text"]
            user_files = user_input["files"]
            
            # Afficher le message utilisateur immédiatement
            add_message("user", user_text)
            st.rerun()  # Forcer le rafraîchissement pour afficher le message utilisateur
            
            # Démarrer le traitement
            set_processing(True, "Initialisation du traitement...", 0.1)
            
            try:
                # Initialisation de l'orchestrateur
                orchestrator = Orchestrator()
                
                # Déterminer le mode et les paramètres appropriés
                mode, mode_params = get_current_mode()
                
                # Construire les arguments pour l'orchestrateur
                orchestration_args = {
                    "query": user_text,
                    "mode": mode,
                    "files": user_files,
                    "ocr_enabled": ocr_enabled
                }
                
                # Ajouter les paramètres spécifiques au mode
                if mode == "sequence":
                    orchestration_args["agent_sequence"] = mode_params
                elif mode == "single":
                    orchestration_args["single_agent"] = mode_params
                
                # Exécuter l'orchestration
                result = orchestrator.orchestrate(**orchestration_args)
                
                # Fin du traitement
                set_processing(False)
                
                # Gestion des erreurs
                if "error" in result:
                    st.error(result["error"])
                    add_message("assistant", f"Erreur: {result['error']}")
                else:
                    # Enregistrer les résultats
                    st.session_state.current_results = result
                    
                    # Ajouter la réponse à l'historique de conversation
                    if "combined" in result:
                        message_attrs = {}
                        
                        # Ajouter les métadonnées du message
                        if "agent_names" in result and "agent_icons" in result:
                            message_attrs["agent_names"] = result["agent_names"]
                            message_attrs["agent_icons"] = result["agent_icons"]
                        elif "agent_name" in result and "agent_icon" in result:
                            message_attrs["agent_name"] = result["agent_name"]
                            message_attrs["agent_icon"] = result["agent_icon"]
                        
                        # Ajouter les informations de débogage
                        if "selection_method" in result:
                            message_attrs["selection_method"] = result["selection_method"]
                        if "router_response" in result:
                            message_attrs["router_response"] = result["router_response"]
                        
                        add_message("assistant", result["combined"], **message_attrs)
                
                # Rafraîchir l'interface
                st.rerun()
                
            except Exception as e:
                # Gestion des exceptions
                set_processing(False)
                st.error(f"Erreur lors du traitement: {str(e)}")
                add_message("assistant", f"Erreur lors du traitement: {str(e)}")
                st.rerun()
    
    # Affichage du pied de page
    render_footer()

if __name__ == "__main__":
    main()