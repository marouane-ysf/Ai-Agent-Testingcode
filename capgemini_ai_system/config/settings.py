"""
Fichier de configuration principal.
Charge les variables d'environnement et définit les paramètres globaux.
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Configuration Azure AI
AZURE_AI_PROJECT_CONNECTION_STRING = os.environ.get("AZURE_AI_PROJECT_CONNECTION_STRING")
AZURE_AI_AGENT_PROJECT_CONNECTION_STRING = os.environ.get("AZURE_AI_AGENT_PROJECT_CONNECTION_STRING")
AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME = os.environ.get("AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME")

# Configuration de l'application
APP_TITLE = "Capgemini AI Multi-Agent System"
APP_ICON = "☘️"
DEBUG_MODE = False  # Mettre à True pour activer le mode debug

# Configuration des agents
AGENT_CONFIG = {
    # Ces valeurs seront définies dans agents.py
}

# Durée maximale d'attente pour les requêtes d'agents (en secondes)
AGENT_TIMEOUT = 120

# Configuration de l'OCR
OCR_ENABLED_BY_DEFAULT = False