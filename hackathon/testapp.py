import streamlit as st
from functions import *
import os
from pathlib import Path

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Capgemini AI Multi-Agent System",
    page_icon="☘️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #003366;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #003366;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .agent-card {
        border: 1px solid #f0f2f6;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        background-color: #f8f9fa;
    }
    .agent-header {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .agent-icon {
        font-size: 1.5rem;
        margin-right: 0.5rem;
    }
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
    .selected-agent {
        border-left: 5px solid #003366;
        font-weight: 600;
    }
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
    .context-info {
        background-color: #e8f4ff;
        padding: 0.5rem;
        border-radius: 5px;
        margin-top: 0.5rem;
        font-size: 0.8rem;
        border-left: 3px solid #0066cc;
    }
</style>
""", unsafe_allow_html=True)

# Titre principal
st.markdown('<div class="main-header">Capgemini AI Multi-Agent System</div>', unsafe_allow_html=True)

# Initialisation des variables de session
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processing" not in st.session_state:
    st.session_state.processing = False
if "orchestration_mode" not in st.session_state:
    st.session_state.orchestration_mode = "intelligent"
if "selected_agents" not in st.session_state:
    st.session_state.selected_agents = []
if "current_results" not in st.session_state:
    st.session_state.current_results = None
if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False
if "router_raw_response" not in st.session_state:
    st.session_state.router_raw_response = ""
if "agent_sequence" not in st.session_state:
    st.session_state.agent_sequence = []
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = []
# Contexte persistant
if "router_thread_id" not in st.session_state:
    st.session_state.router_thread_id = None
if "context_mode" not in st.session_state:
    st.session_state.context_mode = True

# Barre latérale pour la configuration
with st.sidebar:
    # Get the directory of the current script
    current_dir = Path(__file__).parent
    image_path = os.path.join(current_dir, "assets", "capgemini-.png")

    # Display the image with error handling
    try:
        st.image(image_path, width=190)
    except Exception:
        # Fallback if image can't be loaded
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
        for agent_key, agent_info in AGENTS.items():
            if agent_key != "router":
                if st.checkbox(f"{agent_info['icon']} {agent_info['name']}", key=f"seq_{agent_key}"):
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
        for agent_key, agent_info in AGENTS.items():
            if agent_key != "router":
                if st.button(f"{agent_info['icon']} {agent_info['name']}", help=agent_info['description'], key=f"btn_{agent_key}"):
                    st.session_state.selected_agents = [agent_key]

    # Activation/désactivation du mode contexte
    st.session_state.context_mode = st.checkbox("Maintenir le contexte", value=True, 
                                              help="Active/désactive la mémoire des conversations précédentes")
    
    st.session_state.debug_mode = st.checkbox("Mode debug", value=st.session_state.debug_mode)

    if st.session_state.context_mode:
        st.markdown("""
        <div class="context-info">
            Mode contexte activé. Les agents se souviendront des interactions précédentes.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Agents disponibles")
    for agent_key, agent_info in AGENTS.items():
        if agent_key != "router" or st.session_state.orchestration_mode == "intelligent":
            css_class = "agent-card"
            if agent_key in st.session_state.selected_agents:
                css_class += " selected-agent"

            st.markdown(f"""
            <div class="{css_class}">
                <div class="agent-header">{agent_info['icon']} {agent_info['name']}</div>
                <div>{agent_info['description']}</div>
            </div>
            """, unsafe_allow_html=True)

    if st.button("🔄 Réinitialiser la conversation", help="Effacer l'historique de conversation"):
        st.session_state.messages = []
        st.session_state.current_results = None
        st.session_state.agent_sequence = []
        st.session_state.selected_agents = []
        st.session_state.uploaded_file = []
        # Réinitialiser également les threads d'agents
        thread_keys = [key for key in st.session_state.keys() if key.endswith('_thread_id')]
        for key in thread_keys:
            del st.session_state[key]
        st.rerun()

# checkbox pour activer l'OCR
ocr1 = st.checkbox("Check the box to enable OCR to read scanned pdf that are images", key="ocr1")

# Conteneur principal
main_container = st.container()

with main_container:
    discussion_container = st.container()

    with discussion_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="user-message">
                    <b>Vous:</b><br>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                agent_prefix = ""
                if "agent_name" in message and "agent_icon" in message:
                    agent_prefix = f"{message['agent_icon']} <b>{message['agent_name']}:</b><br>"
                else:
                    agent_prefix = "<b>Assistant:</b><br>"

                st.markdown(f"""
                <div class="assistant-message">
                    {agent_prefix}
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)

                if st.session_state.debug_mode and "selection_method" in message:
                    st.markdown(f"""
                    <div class="debug-info">
                        <b>Méthode de sélection:</b> {message["selection_method"]}<br>
                        <b>Réponse brute du Router:</b>
                        <div class="router-response">{message.get("router_response", "Non disponible")}</div>
                    </div>
                    """, unsafe_allow_html=True)

    if st.session_state.processing:
        st.markdown(f"<div style='margin-top: 1rem;'>{st.session_state.progress_text}</div>", unsafe_allow_html=True)
        st.progress(st.session_state.progress_value)

    # Section pour afficher les réponses détaillées des agents individuels en mode expandable
    if st.session_state.current_results and "error" not in st.session_state.current_results:
        if len(st.session_state.selected_agents) > 1:
            with st.expander("📊 Voir les réponses détaillées de chaque agent"):
                cols = st.columns(len(st.session_state.selected_agents))
                
                for i, agent_key in enumerate(st.session_state.selected_agents):
                    if agent_key in st.session_state.current_results:
                        with cols[i]:
                            st.markdown(f"""
                            <div class="agent-card">
                                <div class="agent-header">{AGENTS[agent_key]['icon']} {AGENTS[agent_key]['name']}</div>
                                <div style="max-height: 300px; overflow-y: auto;">
                                    {st.session_state.current_results[agent_key]}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

    # Affichage du contexte actif si mode debug activé
    if st.session_state.debug_mode and st.session_state.context_mode:
        thread_keys = [key for key in st.session_state.keys() if key.endswith('_thread_id')]
        if thread_keys:
            st.markdown("""
            <div class="context-info">
                <b>Threads d'agents actifs:</b><br>
            """, unsafe_allow_html=True)
            for key in thread_keys:
                agent_name = key.replace('_thread_id', '')
                st.markdown(f"• {agent_name}: {st.session_state[key]}<br>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    user_prompt = st.chat_input("Tapez votre message ici...", disabled=st.session_state.processing, accept_file="multiple")
    if user_prompt:
        user_text = user_prompt["text"]
        user_file = user_prompt["files"]

        user_input = prompt_constructor(user_prompt, ocr1)

        if user_input and not st.session_state.processing:
            st.markdown(f"""
            <div class="user-message">
                <b>Vous:</b><br>
                {user_text}
            </div>
            """, unsafe_allow_html=True)

            st.session_state.messages.append({"role": "user", "content": user_text})
            st.session_state.processing = True
            st.session_state.progress_text = "Initialisation du traitement..."
            st.session_state.progress_value = 0.1

            try:
                if st.session_state.orchestration_mode == "intelligent":
                    with st.spinner("Analyse de votre requête et sélection des agents les plus appropriés..."):
                        result = run_async_function(run_orchestrated_workflow, user_input)

                elif st.session_state.orchestration_mode == "sequence":
                    with st.spinner("Les agents collaborent en séquence pour répondre à votre question..."):
                        result = run_async_function(run_sequential_pipeline, user_input)

                else:
                    if st.session_state.selected_agents and all(agent in AGENTS for agent in st.session_state.selected_agents):
                        with st.spinner(f"{', '.join(AGENTS[agent]['name'] for agent in st.session_state.selected_agents)} préparent votre réponse..."):
                            result = run_async_function(run_specific_agent, user_input, st.session_state.selected_agents[0])
                    else:
                        result = {"error": "Veuillez sélectionner un agent dans la barre latérale pour continuer."}

                st.session_state.processing = False

                if "error" in result:
                    st.error(result["error"])
                    st.session_state.messages.append({"role": "assistant", "content": result["error"]})
                else:
                    st.session_state.current_results = result

                    agent_prefix = ""
                    if "agent_names" in result and "agent_icons" in result:
                        agent_prefix = f"{', '.join(result['agent_icons'])} <b>{', '.join(result['agent_names'])}:</b><br>"
                    elif "agent_name" in result and "agent_icon" in result:
                        agent_prefix = f"{result['agent_icon']} <b>{result['agent_name']}:</b><br>"
                    else:
                        agent_prefix = "<b>Assistant:</b><br>"

                    st.markdown(f"""
                    <div class="assistant-message">
                        {agent_prefix}
                        {result["combined"]}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.session_state.debug_mode and "selection_method" in result:
                        st.markdown(f"""
                        <div class="debug-info">
                            <b>Méthode de sélection:</b> {result["selection_method"]}<br>
                            <b>Réponse brute du Router:</b>
                            <div class="router-response">{result.get("router_response", "Non disponible")}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    message_data = {
                        "role": "assistant",
                        "content": result["combined"]
                    }

                    if "agent_names" in result:
                        message_data["agent_names"] = result["agent_names"]
                        message_data["agent_icons"] = result["agent_icons"]
                    elif "agent_name" in result: 
                        message_data["agent_name"] = result["agent_name"]
                        message_data["agent_icon"] = result["agent_icon"]

                    if "selection_method" in result:
                        message_data["selection_method"] = result["selection_method"]
                    if "router_response" in result:
                        message_data["router_response"] = result["router_response"]

                    st.session_state.messages.append(message_data)

                    # Affichage d'un indicateur de contexte si le mode contexte est activé
                    if st.session_state.context_mode and st.session_state.debug_mode:
                        st.markdown("""
                        <div class="context-info">
                            <b>✓ Contexte maintenu</b> - Les agents conservent la mémoire de cette conversation.
                        </div>
                        """, unsafe_allow_html=True)

            except Exception as e:
                st.session_state.processing = False
                st.error(f"Erreur lors du traitement: {str(e)}")
                st.session_state.messages.append({"role": "assistant", "content": f"Erreur lors du traitement: {str(e)}"})

# Pied de page
st.markdown("""
<div style="text-align: center; margin-top: 3rem; color: #666; font-size: 0.8rem;">
    <p>Développé pour Capgemini AI Agents - Système d'Orchestration Intelligente | 2025</p>
</div>
""", unsafe_allow_html=True)