"""
Text chunking implementation for document processing.
"""

from dataclasses import dataclass
from typing import List

from ..pipeline import Document

@dataclass
class ChunkConfig:
    """Configuration for text chunking."""
    chunk_size: int = 500
    chunk_overlap: int = 50

class TextChunker:
    """Splits documents into overlapping chunks."""
    
    def __init__(self, config: ChunkConfig):
        self.config = config
    
    def split(self, doc: Document) -> List[Document]:
        """Split a document into chunks with overlap."""
        text = doc.content
        chunks = []
        
        # If text is shorter than chunk size, return as single chunk
        if len(text) <= self.config.chunk_size:
            return [doc]
        
        # Split into overlapping chunks
        start = 0
        chunk_id = 0
        
        while start < len(text):
            # Calculate end position
            end = start + self.config.chunk_size
            
            # If this is not the first chunk, include overlap
            if start > 0:
                start = start - self.config.chunk_overlap
            
            # If this is the last chunk, include all remaining text
            if end >= len(text):
                end = len(text)
            
            # Extract chunk text
            chunk_text = text[start:end]
            
            # Create chunk document
            chunk = Document(
                id=f"{doc.id}_chunk_{chunk_id}",
                content=chunk_text,
                metadata={
                    **doc.metadata,
                    "chunk_id": chunk_id,
                    "parent_id": doc.id,
                    "start": start,
                    "end": end
                }
            )
            
            chunks.append(chunk)
            chunk_id += 1
            
            # Move to next chunk
            start = end
        
        return chunks