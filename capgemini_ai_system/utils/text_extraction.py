"""
Utilitaires pour l'extraction de texte à partir de différents types de documents.
"""

import io
import fitz  # PyMuPDF
from PyPDF2 import PdfReader
from typing import List, Dict, Any, Optional, Tuple, BinaryIO
import streamlit as st

def extract_text_from_pdf(file_object: BinaryIO, use_ocr: bool = False) -> str:
    """
    Extrait le texte d'un fichier PDF.
    
    Args:
        file_object: L'objet fichier PDF
        use_ocr: Indique si l'OCR doit être utilisé pour les images
        
    Returns:
        Le texte extrait du PDF
    """
    try:
        if use_ocr:
            # Utiliser PyMuPDF avec OCR
            file_content = file_object.read()
            pdf_document = fitz.open(stream=file_content, filetype="pdf")
            text = ""
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                text += page.get_text()
            return text
        else:
            # Utiliser PyPDF2 pour l'extraction standard
            reader = PdfReader(file_object)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:  # Vérifier que l'extraction a fonctionné
                    text += page_text + "\n"
            
            # Si PyPDF2 n'a pas pu extraire de texte, essayer PyMuPDF
            if not text.strip():
                file_object.seek(0)  # Réinitialiser la position dans le fichier
                file_content = file_object.read()
                pdf_document = fitz.open(stream=file_content, filetype="pdf")
                text = ""
                for page_num in range(pdf_document.page_count):
                    page = pdf_document.load_page(page_num)
                    text += page.get_text()
            
            return text
    except Exception as e:
        st.error(f"Erreur lors de l'extraction du texte du PDF: {str(e)}")
        return f"Erreur d'extraction: {str(e)}"

def extract_text_from_text_file(file_object: BinaryIO) -> str:
    """
    Extrait le texte d'un fichier texte.
    
    Args:
        file_object: L'objet fichier texte
        
    Returns:
        Le contenu du fichier texte
    """
    try:
        content = file_object.read()
        # Essayer de décoder avec utf-8
        try:
            return content.decode('utf-8')
        except UnicodeDecodeError:
            # Fallback sur latin-1 (devrait fonctionner pour tout fichier binaire)
            return content.decode('latin-1')
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier texte: {str(e)}")
        return f"Erreur de lecture: {str(e)}"

def extract_text_from_file(uploaded_file: Any, use_ocr: bool = False) -> Tuple[str, str]:
    """
    Extrait le texte d'un fichier téléchargé, quel que soit son type.
    
    Args:
        uploaded_file: Le fichier téléchargé via Streamlit
        use_ocr: Indique si l'OCR doit être utilisé pour les PDFs
        
    Returns:
        Tuple[str, str]: Le texte extrait et le nom du fichier
    """
    if uploaded_file is None:
        return "", ""
    
    file_name = uploaded_file.name
    file_type = uploaded_file.type
    
    try:
        if file_type == "application/pdf":
            extracted_text = extract_text_from_pdf(uploaded_file, use_ocr)
        elif file_type == "text/plain":
            extracted_text = extract_text_from_text_file(uploaded_file)
        else:
            extracted_text = f"Type de fichier non pris en charge: {file_type}"
            st.warning(f"Le type de fichier {file_type} n'est pas pris en charge pour l'extraction de texte.")
        
        return extracted_text, file_name
    except Exception as e:
        st.error(f"Erreur lors de l'extraction du texte de {file_name}: {str(e)}")
        return f"Erreur: {str(e)}", file_name

def extract_text_from_multiple_files(files: List[Any], use_ocr: bool = False) -> List[Dict[str, str]]:
    """
    Extrait le texte de plusieurs fichiers téléchargés.
    
    Args:
        files: Liste des fichiers téléchargés via Streamlit
        use_ocr: Indique si l'OCR doit être utilisé pour les PDFs
        
    Returns:
        Liste de dictionnaires contenant le contenu et le nom de chaque fichier
    """
    results = []
    
    for i, file in enumerate(files):
        # Affichage du progrès dans Streamlit
        st.text(f"Traitement du fichier {i+1}/{len(files)}: {file.name}")
        
        extracted_text, file_name = extract_text_from_file(file, use_ocr)
        results.append({
            'content': extracted_text,
            'name': file_name
        })
    
    return results