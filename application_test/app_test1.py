import streamlit as st
import time
from azure.ai.projects import AIProjectClient

# Configuration de la page Streamlit
st.set_page_config(page_title="Azure AI Agent Chat", page_icon="🤖")
st.title("Chat avec votre Agent Azure AI")

# Initialisation des variables de session
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

# Fonction pour initialiser le client Azure AI avec chaîne de connexion
@st.cache_resource
def get_client(conn_str):
    try:
        client = AIProjectClient.from_connection_string(conn_str=conn_str)
        return client
    except Exception as e:
        st.error(f"Erreur d'initialisation du client: {e}")
        return None

# Fonction pour récupérer l'agent
@st.cache_data
def get_agent(client, agent_id):
    try:
        agent = client.agents.get_agent(agent_id)
        return agent
    except Exception as e:
        st.error(f"Erreur lors de la récupération de l'agent: {e}")
        return None

# Fonction pour créer un thread s'il n'existe pas
def ensure_thread(client):
    if st.session_state.thread_id is None:
        try:
            thread = client.agents.create_thread()
            st.session_state.thread_id = thread.id
            return thread.id
        except Exception as e:
            st.error(f"Erreur lors de la création du thread: {e}")
            return None
    return st.session_state.thread_id

# Fonction pour envoyer un message et obtenir une réponse
def send_message_and_get_response(client, agent_id, thread_id, user_message):
    try:
        # Envoi du message utilisateur
        client.agents.create_message(
            thread_id=thread_id,
            role="user",
            content=user_message
        )
        
        # Lancement du traitement par l'agent
        run = client.agents.create_and_process_run(
            thread_id=thread_id,
            agent_id=agent_id
        )
        
        # Attente que l'agent traite le message
        with st.spinner("L'agent réfléchit..."):
            # Attente initiale
            time.sleep(3)
            
            # Récupération des messages après traitement
            messages = client.agents.list_messages(thread_id=thread_id)
            
            # Tri des messages par timestamp
            if hasattr(messages, "data") and messages.data:
                sorted_messages = sorted(messages.data, key=lambda x: x.created_at)
                
                # Récupération du dernier message (réponse de l'agent)
                latest_message = sorted_messages[-1]
                
                if latest_message.role == "assistant" and latest_message.content:
                    response_text = ""
                    for content_item in latest_message.content:
                        if content_item["type"] == "text":
                            response_text += content_item["text"]["value"]
                    return response_text
                
        return "Désolé, je n'ai pas pu obtenir une réponse de l'agent."
        
    except Exception as e:
        return f"Erreur lors de la communication avec l'agent: {e}"

# Barre latérale pour la configuration
with st.sidebar:
    st.header("Configuration")
    conn_string = st.text_input(
        "Chaîne de connexion",
        value="eastus2.api.azureml.ms;85b3c2ee-1663-46a0-8409-975637a61fcd;azur;marouaneyoussoufi-6059"
    )
    agent_id = st.text_input("ID de l'Agent", value="asst_F88GnWL62ahTUjr1w7N3Gw4X")
    
    if st.button("Réinitialiser la conversation"):
        st.session_state.messages = []
        st.session_state.thread_id = None
        st.experimental_rerun()

# Initialisation du client avec la chaîne de connexion
client = get_client(conn_string)

if client:
    # Récupération de l'agent
    agent = get_agent(client, agent_id)
    
    if agent:
        st.sidebar.success(f"Agent connecté: {agent.name}")
        
        # Assurer l'existence d'un thread
        thread_id = ensure_thread(client)
        
        if thread_id:
            # Affichage des messages précédents
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
            
            # Champ de saisie pour le nouveau message
            user_input = st.chat_input("Tapez votre message ici...")
            
            if user_input:
                # Affichage du message utilisateur
                with st.chat_message("user"):
                    st.write(user_input)
                
                # Sauvegarde du message utilisateur
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                # Obtention de la réponse
                response = send_message_and_get_response(client, agent_id, thread_id, user_input)
                
                # Affichage de la réponse
                with st.chat_message("assistant"):
                    st.write(response)
                
                # Sauvegarde de la réponse
                st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            st.error("Impossible de créer un thread de conversation.")
    else:
        st.error(f"Agent avec l'ID {agent_id} non trouvé.")
else:
    st.error("Impossible d'initialiser le client Azure AI. Veuillez vérifier votre chaîne de connexion.")

# Ajout d'un pied de page
st.markdown("---")
st.markdown("Développé avec ❤️ pour Azure AI Agents")