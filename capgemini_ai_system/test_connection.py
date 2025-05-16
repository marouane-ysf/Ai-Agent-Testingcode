import asyncio
import os
import time
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from semantic_kernel.agents import AzureAIAgent

async def test_connection():
    # Charger les variables d'environnement
    load_dotenv()
    
    # Récupérer les valeurs
    connection_string = os.environ.get("AZURE_AI_PROJECT_CONNECTION_STRING")
    agent_id = os.environ.get("QUALITY_AGENT_ID")
    
    print(f"Connection string: {connection_string[:20]}...{connection_string[-8:]}")
    print(f"Agent ID: {agent_id}")
    
    try:
        print("Création des credentials...")
        credential = DefaultAzureCredential()
        
        print("Initialisation du client...")
        client = AzureAIAgent.create_client(credential=credential)
        print("Client créé avec succès!")
        
        print("Création d'un thread...")
        # IMPORTANT: Utilisez await ici
        thread = await client.agents.create_thread()
        thread_id = thread.id
        print(f"Thread créé: {thread_id}")
        
        print("Ajout d'un message simple...")
        await client.agents.create_message(
            thread_id=thread_id,
            role="user",
            content="Bonjour, pouvez-vous répondre à ce message simple?"
        )
        
        print(f"Exécution de l'agent: {agent_id}")
        run = await client.agents.create_run(
            thread_id=thread_id,
            agent_id=agent_id
        )
        
        print("Attente de la réponse...")
        while True:
            run = await client.agents.get_run(thread_id=thread_id, run_id=run.id)
            print(f"Statut: {run.status}")
            if run.status == "completed":
                break
            elif run.status in ["failed", "cancelled", "expired"]:
                print(f"Échec: {run.status}")
                break
            await asyncio.sleep(2)
        
        print("Récupération des messages...")
        messages = await client.agents.list_messages(thread_id=thread_id)
        
        print("\n--- CONVERSATION ---")
        for msg in messages.data:
            print(f"{msg.role.upper()}:")
            if msg.content:
                for content in msg.content:
                    if content.type == "text":
                        print(f"  {content.text.value}")
            print()
            
    except Exception as e:
        print(f"ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Cette ligne est CRUCIALE
    asyncio.run(test_connection())