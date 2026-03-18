"""
PDF Loading Module

Extracts text from PDF files with metadata preservation.
Uses pdfplumber for robust text extraction.

Why pdfplumber over PyPDFLoader?
- Better handling of complex layouts
- Preserves table structures
- More accurate text positioning
- Access to page-level metadata
"""

from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
import pdfplumber
import logging

logger = logging.getLogger(__name__)


@dataclass
class PageContent:
    """
    Represents extracted content from a single PDF page.
    
    Attributes:
        text: The extracted text content
        metadata: Dictionary containing source info (filename, page_number, etc.)
    """
    text: str
    metadata: Dict[str, Any]


class PDFLoader:
    """
    Loads and extracts text from PDF files.
    
    Each page is returned as a separate PageContent object,
    preserving the source information needed for citations.
    """
    
    def __init__(self):
        """Initialize the PDF loader."""
        pass  
    
    def load(self, file_path: Path) -> List[PageContent]:
        """
        Load a PDF file and extract text from each page.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of PageContent objects, one per page
            
        Raises:
            FileNotFoundError: If the PDF doesn't exist
            ValueError: If the file is not a valid PDF
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"PDF not found: {file_path}")
        
        if file_path.suffix.lower() != ".pdf":
            raise ValueError(f"Not a PDF file: {file_path}")
        
        pages = []
        
        try:
            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)
                logger.info(f"Loading {file_path.name} ({total_pages} pages)")
                
                for page_num, page in enumerate(pdf.pages, start=1):
                    # Extract text from page
                    text = page.extract_text() or ""
                    
                    # Skip empty pages
                    if not text.strip():
                        logger.debug(f"Skipping empty page {page_num}")
                        continue
                    
                    # Build metadata for citations
                    metadata = {
                        "source": file_path.name,
                        "source_path": str(file_path.absolute()),
                        "page": page_num,
                        "total_pages": total_pages,
                    }
                    
                    pages.append(PageContent(text=text, metadata=metadata))
                    
        except Exception as e:
            raise ValueError(f"Failed to parse PDF {file_path}: {e}")
        
        logger.info(f"Extracted {len(pages)} pages with content from {file_path.name}")
        return pages
      
    
    
    
    
    
    
    def load_directory(self, directory: Path) -> List[PageContent]:
        """
        Load all PDF files from a directory.
        
        Args:
            directory: Path to directory containing PDFs
            
        Returns:
            Combined list of PageContent from all PDFs
        """
        directory = Path(directory)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        if not directory.is_dir():
            raise ValueError(f"Not a directory: {directory}")
        
        pdf_files = sorted(directory.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {directory}")
            return []
        
        logger.info(f"Found {len(pdf_files)} PDF files in {directory}")
        
        all_pages = []
        for pdf_path in pdf_files:
            try:
                pages = self.load(pdf_path)
                all_pages.extend(pages)
            except Exception as e:
                logger.error(f"Failed to load {pdf_path.name}: {e}")
                continue
        
        return all_pages