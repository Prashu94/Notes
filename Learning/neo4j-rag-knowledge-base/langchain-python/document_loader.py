"""
Document loader for PDF and TXT files with multimodal support
"""
import os
from pathlib import Path
from typing import List, Optional, Union
from langchain.schema import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    DirectoryLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultimodalDocumentLoader:
    """Load and process PDF and TXT documents"""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        supported_extensions: tuple = (".pdf", ".txt")
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.supported_extensions = supported_extensions
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_single_file(self, file_path: Union[str, Path]) -> List[Document]:
        """
        Load a single document file
        
        Args:
            file_path: Path to the document file
            
        Returns:
            List of Document objects
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        extension = file_path.suffix.lower()
        
        if extension not in self.supported_extensions:
            raise ValueError(
                f"Unsupported file type: {extension}. "
                f"Supported types: {self.supported_extensions}"
            )
        
        try:
            if extension == ".pdf":
                loader = PyPDFLoader(str(file_path))
            elif extension == ".txt":
                loader = TextLoader(str(file_path), encoding="utf-8")
            else:
                raise ValueError(f"Unsupported extension: {extension}")
            
            documents = loader.load()
            
            # Add source metadata
            for doc in documents:
                doc.metadata["source"] = str(file_path)
                doc.metadata["file_name"] = file_path.name
                doc.metadata["file_type"] = extension[1:]  # Remove dot
            
            logger.info(f"Loaded {len(documents)} pages from {file_path}")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading {file_path}: {str(e)}")
            raise
    
    def load_directory(self, directory_path: Union[str, Path]) -> List[Document]:
        """
        Load all supported documents from a directory
        
        Args:
            directory_path: Path to directory containing documents
            
        Returns:
            List of Document objects
        """
        directory_path = Path(directory_path)
        
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        documents = []
        
        for ext in self.supported_extensions:
            files = list(directory_path.glob(f"*{ext}"))
            logger.info(f"Found {len(files)} {ext} files in {directory_path}")
            
            for file_path in files:
                try:
                    docs = self.load_single_file(file_path)
                    documents.extend(docs)
                except Exception as e:
                    logger.error(f"Skipping {file_path}: {str(e)}")
        
        logger.info(f"Total documents loaded: {len(documents)}")
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of chunked Document objects
        """
        chunks = self.text_splitter.split_documents(documents)
        
        # Add chunk metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = i
            chunk.metadata["chunk_size"] = len(chunk.page_content)
        
        logger.info(f"Split into {len(chunks)} chunks")
        return chunks
    
    def load_and_split(
        self,
        path: Union[str, Path],
        is_directory: bool = True
    ) -> List[Document]:
        """
        Load and split documents in one step
        
        Args:
            path: Path to file or directory
            is_directory: Whether the path is a directory
            
        Returns:
            List of chunked Document objects
        """
        if is_directory:
            documents = self.load_directory(path)
        else:
            documents = self.load_single_file(path)
        
        return self.split_documents(documents)


class DocumentMetadataExtractor:
    """Extract and enrich document metadata"""
    
    @staticmethod
    def extract_metadata(document: Document) -> dict:
        """
        Extract comprehensive metadata from document
        
        Args:
            document: Document object
            
        Returns:
            Dictionary of metadata
        """
        metadata = document.metadata.copy()
        
        # Add content statistics
        content = document.page_content
        metadata.update({
            "word_count": len(content.split()),
            "char_count": len(content),
            "line_count": len(content.split("\n")),
        })
        
        return metadata
    
    @staticmethod
    def add_custom_metadata(
        document: Document,
        custom_data: dict
    ) -> Document:
        """
        Add custom metadata to document
        
        Args:
            document: Document object
            custom_data: Dictionary of custom metadata
            
        Returns:
            Document with updated metadata
        """
        document.metadata.update(custom_data)
        return document
