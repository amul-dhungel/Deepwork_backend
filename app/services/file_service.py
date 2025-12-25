"""
File processing service for document extraction.
"""

import os
import PyPDF2
from typing import Dict, Tuple

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False
    print("Warning: python-docx not installed. DOCX support disabled.")


class FileService:
    """Handles file processing and metadata extraction."""
    
    @staticmethod
    def process_file(file_path: str, original_filename: str) -> Tuple[str, Dict]:
        """
        Process uploaded file and extract text and metadata.
        
        Args:
            file_path: Path to saved file
            original_filename: Original filename
            
        Returns:
            Tuple of (extracted_text, metadata_dict)
        """
        file_text = ""
        abstract_summary = "No abstract content detected."
        year = "2024"
        author = "Unknown Author"
        title = original_filename
        
        filename_lower = original_filename.lower()
        
        # Process PDF
        if filename_lower.endswith('.pdf'):
            file_text, metadata = FileService._process_pdf(file_path)
            author = metadata.get('author', author)
            title = metadata.get('title', title)
            abstract_summary = FileService._extract_abstract(file_text)
        
        # Process TXT
        elif filename_lower.endswith('.txt'):
            file_text = FileService._process_txt(file_path)
            abstract_summary = file_text[:300].strip() + "..."
        
        # Process DOCX
        elif filename_lower.endswith('.docx'):
            if HAS_DOCX:
                file_text, metadata = FileService._process_docx(file_path)
                author = metadata.get('author', author)
                title = metadata.get('title', title)
                abstract_summary = file_text[:300].strip() + "..."
            else:
                file_text = "[DOCX support disabled on server]\n"
                abstract_summary = "DOCX processing disabled."
        
        # Build metadata
        citation = f"{author} ({year}). *{title}*."
        
        metadata_dict = {
            "name": original_filename,
            "author": author,
            "title": title,
            "citation": citation,
            "summary": abstract_summary,
            "size": os.path.getsize(file_path)
        }
        
        return file_text, metadata_dict
    
    @staticmethod
    def _process_pdf(file_path: str) -> Tuple[str, Dict]:
        """Extract text and metadata from PDF."""
        text = ""
        metadata = {}
        
        try:
            reader = PyPDF2.PdfReader(file_path)
            
            # Extract metadata
            if reader.metadata:
                if reader.metadata.get('/Author'):
                    metadata['author'] = reader.metadata.get('/Author')
                if reader.metadata.get('/Title'):
                    metadata['title'] = reader.metadata.get('/Title')
            
            # Extract text from all pages
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
                    
        except Exception as e:
            print(f"Error reading PDF: {e}")
        
        return text, metadata
    
    @staticmethod
    def _process_txt(file_path: str) -> str:
        """Extract text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading TXT: {e}")
            return ""
    
    @staticmethod
    def _process_docx(file_path: str) -> Tuple[str, Dict]:
        """Extract text and metadata from DOCX."""
        text = ""
        metadata = {}
        
        try:
            doc = Document(file_path)
            
            # Extract metadata
            if doc.core_properties.author:
                metadata['author'] = doc.core_properties.author
            if doc.core_properties.title:
                metadata['title'] = doc.core_properties.title
            
            # Extract text
            text = "\n".join([para.text for para in doc.paragraphs])
            
        except Exception as e:
            print(f"Error reading DOCX: {e}")
            text = f"[Error processing DOCX: {e}]\n"
        
        return text, metadata
    
    @staticmethod
    def _extract_abstract(text: str) -> str:
        """Try to extract abstract from document text."""
        text_start = text[:2000]
        
        if "Abstract" in text_start:
            parts = text_start.split("Abstract")
            if len(parts) > 1:
                return parts[1][:500].strip() + "..."
        
        return text[:300].strip() + "..."


# Singleton instance
_file_service = None


def get_file_service() -> FileService:
    """Get or create file service instance."""
    global _file_service
    if _file_service is None:
        _file_service = FileService()
    return _file_service
