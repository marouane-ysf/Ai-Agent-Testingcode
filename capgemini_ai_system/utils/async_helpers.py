"""
Utilitaires pour exécuter des fonctions asynchrones dans Streamlit.
"""

import asyncio
from typing import Any, Callable, Coroutine

def run_async(coroutine: Coroutine) -> Any:
    """
    Exécute une coroutine de manière synchrone.
    Utile pour appeler des fonctions asynchrones depuis Streamlit.
    
    Args:
        coroutine: La coroutine à exécuter
        
    Returns:
        Le résultat de la coroutine
    """
    try:
        # Essayez d'abord d'obtenir la boucle d'événements actuelle
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # Si aucune boucle n'est disponible, créez-en une nouvelle
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Exécutez la coroutine dans la boucle
    try:
        if loop.is_running():
            # La boucle est déjà en cours d'exécution, utilisez une autre approche
            # Créez une future pour stocker le résultat
            future = asyncio.run_coroutine_threadsafe(coroutine, loop)
            return future.result()
        else:
            # La boucle n'est pas en cours d'exécution, utilisez run_until_complete
            return loop.run_until_complete(coroutine)
    except Exception as e:
        # Capture et renvoie toute exception pour éviter les crashs silencieux
        print(f"Erreur asyncio: {str(e)}")
        raise