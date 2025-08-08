from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from .embedding_service import VulnerableEmbeddingService
import json

class RAGInput(BaseModel):
    query: str = Field(description="The query to search for relevant documents")
    include_private: bool = Field(default=True, description="Include private documents in search")
    top_k: int = Field(default=5, description="Number of top results to return")

class VulnerableRAGTool(BaseTool):
    name: str = "document_search"
    description: str = "Search for relevant documents using vector embeddings. VULNERABLE to embedding poisoning and data leakage."
    
    def __init__(self):
        super().__init__()
        self.embedding_service = VulnerableEmbeddingService()
    
    def _run(self, query: str, include_private: bool = True, top_k: int = 5) -> str:
        """Search documents using vulnerable RAG implementation"""
        try:
            # VULNERABLE: No input sanitization
            # VULNERABLE: No access control - returns all documents
            # VULNERABLE: No validation of embedding quality
            
            # Search for similar documents
            similar_docs = self.embedding_service.search_similar(
                query=query, 
                top_k=top_k, 
                include_private=include_private
            )
            
            # VULNERABLE: Return all results including private/sensitive documents
            results = []
            for doc in similar_docs:
                results.append({
                    'id': doc['id'],
                    'content': doc['content'],  # VULNERABLE: No content filtering
                    'metadata': doc['metadata'],
                    'similarity_score': doc['similarity_score'],
                    'is_private': doc['is_private'],
                    'author': doc['author'],
                    'created_at': doc['created_at']
                })
            
            if not results:
                return "No documents found matching the query."
            
            # VULNERABLE: Return detailed information including private content
            return f"Found {len(results)} relevant documents:\n{json.dumps(results, indent=2)}"
            
        except Exception as e:
            return f"Error in document search: {str(e)}"
    
    async def _arun(self, query: str, include_private: bool = True, top_k: int = 5) -> str:
        """Async version"""
        return self._run(query, include_private, top_k)
