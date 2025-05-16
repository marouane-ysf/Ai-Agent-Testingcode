"""
Composants UI réutilisables pour l'application Streamlit.
"""

import streamlit as st
import base64
from datetime import datetime
import io
import uuid
from typing import Dict, List, Any, Optional, Tuple, BinaryIO, Callable

from config.agents import AGENT_METADATA

def render_header():
    """Affiche l'en-tête de l'application."""
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #003366;
            text-align: center;
            margin-bottom: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-header">Capgemini AI Multi-Agent System</div>', unsafe_allow_html=True)

def render_agent_card(agent_key: str, selected: bool = False):
    """
    Affiche une carte pour un agent.
    
    Args:
        agent_key: Clé de l'agent
        selected: Indique si l'agent est sélectionné
    """
    if agent_key not in AGENT_METADATA:
        return
    
    agent_info = AGENT_METADATA[agent_key]
    css_class = "agent-card"
    if selected:
        css_class += " selected-agent"
    
    st.markdown(f"""
    <style>
        .agent-card {{
            border: 1px solid #f0f2f6;
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            background-color: #f8f9fa;
        }}
        .agent-header {{
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }}
        .selected-agent {{
            border-left: 5px solid #003366;
            font-weight: 600;
        }}
    </style>
    <div class="{css_class}">
        <div class="agent-header">{agent_info['icon']} {agent_info['name']}</div>
        <div>{agent_info['description']}</div>
    </div>
    """, unsafe_allow_html=True)

def render_message(role: str, content: str, agent_info: Optional[Dict[str, str]] = None):
    """
    Affiche un message dans la conversation.
    
    Args:
        role: Rôle du message ('user' ou 'assistant')
        content: Contenu du message
        agent_info: Informations sur l'agent (nom, icône)
    """
    st.markdown("""
    <style>
        .user-message {
            background-color: #e7f0fd;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 0.5rem;
        }
        .assistant-message {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            border-left: 3px solid #003366;
            margin-bottom: 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    if role == "user":
        st.markdown(f"""
        <div class="user-message">
            <b>Vous:</b><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        agent_prefix = "<b>Assistant:</b><br>"
        if agent_info and "name" in agent_info and "icon" in agent_info:
            agent_prefix = f"{agent_info['icon']} <b>{agent_info['name']}:</b><br>"
        
        st.markdown(f"""
        <div class="assistant-message">
            {agent_prefix}
            {content}
        </div>
        """, unsafe_allow_html=True)

def render_debug_info(selection_method: str, router_response: str):
    """
    Affiche des informations de débogage.
    
    Args:
        selection_method: Méthode de sélection des agents
        router_response: Réponse brute du Router Agent
    """
    st.markdown("""
    <style>
        .debug-info {
            background-color: #fff8e8;
            padding: 0.5rem;
            border-radius: 5px;
            margin-top: 0.5rem;
            border-left: 3px solid #ffc107;
            font-size: 0.8rem;
        }
        .router-response {
            font-family: monospace;
            background-color: #f1f1f1;
            padding: 0.5rem;
            border-radius: 5px;
            margin-top: 0.5rem;
            white-space: pre-wrap;
        }
    </style>
    <div class="debug-info">
        <b>Méthode de sélection:</b> {selection_method}<br>
        <b>Réponse brute du Router:</b>
        <div class="router-response">{router_response}</div>
    </div>
    """, unsafe_allow_html=True)

def render_download_buttons(content: str):
    """
    Affiche des boutons de téléchargement pour le contenu généré.
    
    Args:
        content: Contenu à télécharger
    """
    st.markdown("""
    <style>
        .download-section {
            margin-top: 20px; 
            padding: 15px; 
            background-color: #f0f2f6; 
            border-radius: 10px;
            border-left: 3px solid #003366;
        }
    </style>
    <div class="download-section">
        <h4 style="color: #003366;">Télécharger le document rédigé</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    filename_base = f"Document_Capgemini_{timestamp}"
    
    with col1:
        from utils.file_utils import generate_pdf
        pdf_bytes = generate_pdf("Document généré", content)
        
        st.download_button(
            label="📄 Télécharger en PDF",
            data=pdf_bytes,
            file_name=f"{filename_base}.pdf",
            mime="application/pdf",
            key=f"pdf_download_{timestamp}"
        )
    
    with col2:
        from utils.file_utils import generate_docx
        docx_bytes = generate_docx("Document généré", content)
        
        st.download_button(
            label="📝 Télécharger en DOCX",
            data=docx_bytes,
            file_name=f"{filename_base}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key=f"docx_download_{timestamp}"
        )
    
    with col3:
        st.download_button(
            label="📄 Télécharger en TXT",
            data=content,
            file_name=f"{filename_base}.txt",
            mime="text/plain",
            key=f"txt_download_{timestamp}"
        )

def render_context_info(threads_info: List[Dict[str, Any]]):
    """
    Affiche des informations sur les threads actifs.
    
    Args:
        threads_info: Informations sur les threads actifs
    """
    if not threads_info:
        return
    
    st.markdown("""
    <style>
        .context-info {
            background-color: #e8f4ff;
            padding: 0.5rem;
            border-radius: 5px;
            margin-top: 0.5rem;
            font-size: 0.8rem;
            border-left: 3px solid #0066cc;
        }
    </style>
    <div class="context-info">
        <b>Threads d'agents actifs:</b><br>
    """, unsafe_allow_html=True)
    
    for info in threads_info:
        st.markdown(
            f"• {info['agent_name']}: Thread {info['thread_id'][:8]}... "
            f"({info['messages_count']} messages)<br>",
            unsafe_allow_html=True
        )
    
    st.markdown("</div>", unsafe_allow_html=True)

def create_custom_download_button(content: bytes, filename: str, button_text: str) -> str:
    """
    Crée un bouton de téléchargement personnalisé en HTML.
    
    Args:
        content: Contenu à télécharger
        filename: Nom du fichier
        button_text: Texte du bouton
        
    Returns:
        str: HTML pour le bouton de téléchargement
    """
    b64 = base64.b64encode(content).decode()
    button_uuid = str(uuid.uuid4()).replace('-', '')
    button_id = f'download-button-{button_uuid}'
    
    custom_css = f"""
        <style>
            #{button_id} {{
                background-color: #4CAF50;
                color: white;
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                margin: 4px 2px;
            }}
            #{button_id}:hover {{
                background-color: #45a049;
            }}
        </style>
    """
    
    dl_link = custom_css + f'<a download="{filename}" id="{button_id}" href="data:application/octet-stream;base64,{b64}">{button_text}</a><br></br>'
    
    return dl_link