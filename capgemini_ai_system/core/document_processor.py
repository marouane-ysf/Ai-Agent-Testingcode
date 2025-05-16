"""
Processeur de documents pour extraire et formater le contenu des fichiers.
"""

import streamlit as st
from typing import List, Dict, Any, Optional, Tuple, BinaryIO
import asyncio

from utils.text_extraction import extract_text_from_file, extract_text_from_multiple_files

class DocumentProcessor:
    """
    Processeur pour l'extraction et le traitement des documents.
    """
    
    def __init__(self):
        """Initialise le processeur de documents."""
        # Initialiser les variables de session si nécessaires
        if 'processed_documents' not in st.session_state:
            st.session_state.processed_documents = []
    
    async def process_documents(
        self, 
        query: str, 
        files: List[Any], 
        use_ocr: bool = False
    ) -> str:
        """
        Traite les documents et enrichit la requête avec leur contenu.
        
        Args:
            query: La requête utilisateur originale
            files: Liste des fichiers uploadés
            use_ocr: Indique si l'OCR doit être utilisé
            
        Returns:
            str: La requête enrichie avec le contenu des documents
        """
        if not files:
            return query
        
        # Extraction du texte des documents (simuler async avec sleep)
        await asyncio.sleep(0)  # Permet à Streamlit de mettre à jour l'interface
        documents = extract_text_from_multiple_files(files, use_ocr)
        
        # Stocker les documents traités dans la session
        st.session_state.processed_documents = documents
        
        # Enrichir la requête avec le contenu des documents
        enhanced_query = query + "\n\n"
        enhanced_query += "Documents attachés:\n"
        
        for i, doc in enumerate(documents):
            # Limiter la taille du texte pour éviter les dépassements de capacité des agents
            doc_content = doc['content']
            if len(doc_content) > 10000:  # Limiter à environ 10 000 caractères par document
                doc_content = doc_content[:9800] + "...[CONTENU TRONQUÉ]..."
            
            enhanced_query += f"\n--- DOCUMENT {i+1}: {doc['name']} ---\n{doc_content}\n"
        
        return enhanced_query
    
    def get_document_summaries(self) -> List[Dict[str, str]]:
        """
        Récupère un résumé des documents traités.
        
        Returns:
            List[Dict[str, str]]: Résumé des documents avec nom et aperçu
        """
        summaries = []
        
        for doc in st.session_state.get('processed_documents', []):
            # Créer un aperçu limité à 200 caractères
            preview = doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content']
            
            summaries.append({
                'name': doc['name'],
                'preview': preview,
                'size': f"{len(doc['content'])} caractères"
            })
        
        return summaries
    
    def clear_documents(self) -> None:
        """Efface les documents traités de la session."""
        st.session_state.processed_documents = []
    
    def format_document_for_agent(
        self, 
        document_index: int, 
        max_length: int = 8000
    ) -> Optional[str]:
        """
        Formate un document spécifique pour un agent.
        
        Args:
            document_index: L'index du document
            max_length: Longueur maximale du contenu
            
        Returns:
            Optional[str]: Le document formaté, ou None si l'index est invalide
        """
        docs = st.session_state.get('processed_documents', [])
        
        if document_index < 0 or document_index >= len(docs):
            return None
        
        doc = docs[document_index]
        content = doc['content']
        
        # Tronquer si nécessaire
        if len(content) > max_length:
            content = content[:max_length-100] + "...[CONTENU TRONQUÉ]..."
        
        formatted = f"Document: {doc['name']}\n\n{content}"
        return formatted
    
    def construct_prompt_with_documents(
        self, 
        query: str, 
        document_indices: Optional[List[int]] = None,
        prompt_template: Optional[str] = None
    ) -> str:
        """
        Construit un prompt pour l'agent incluant des documents spécifiques.
        
        Args:
            query: La requête utilisateur
            document_indices: Liste des indices des documents à inclure (None pour tous)
            prompt_template: Template de prompt à utiliser
            
        Returns:
            str: Le prompt construit
        """
        docs = st.session_state.get('processed_documents', [])
        
        if not docs:
            return query
        
        # Déterminer quels documents inclure
        if document_indices is None:
            # Inclure tous les documents
            indices = range(len(docs))
        else:
            # Filtrer les indices valides
            indices = [i for i in document_indices if 0 <= i < len(docs)]
        
        # Construire le prompt
        if prompt_template:
            # Utiliser le template fourni
            documents_text = ""
            for i in indices:
                doc = docs[i]
                documents_text += f"\n--- DOCUMENT {i+1}: {doc['name']} ---\n{doc['content']}\n"
            
            # Remplacer les placeholders dans le template
            prompt = prompt_template.replace("{{query}}", query)
            prompt = prompt.replace("{{documents}}", documents_text)
        else:
            # Utiliser un format standard
            prompt = f"{query}\n\nDocuments attachés:"
            for i in indices:
                doc = docs[i]
                # Limiter la taille pour éviter les dépassements
                content = doc['content']
                if len(content) > 8000:
                    content = content[:7800] + "...[CONTENU TRONQUÉ]..."
                prompt += f"\n--- DOCUMENT {i+1}: {doc['name']} ---\n{content}\n"
        
        return prompt