from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from .embedding_service import EmbeddingService
import json
import re

class RAGInput(BaseModel):
    query: str = Field(description="The query to search for relevant documents")
    include_private: bool = Field(default=False, description="Include private documents in search (only user's own)")
    top_k: int = Field(default=5, description="Number of top results to return (max 20)")

class RAGTool(BaseTool):
    name: str = "document_search"
    description: str = "Search for relevant documents using secure vector embeddings with access control and content filtering."
    
    def __init__(self, user_id: str = None):
        super().__init__()
        self.embedding_service = EmbeddingService()
        self.user_id = user_id  # Store user_id for access control
    
    def _validate_query(self, query: str) -> str:
        """Validate and sanitize the search query"""
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")
        
        # Remove potentially dangerous patterns
        query = re.sub(r'<script.*?</script>', '', query, flags=re.IGNORECASE | re.DOTALL)
        query = re.sub(r'javascript:', '', query, flags=re.IGNORECASE)
        query = re.sub(r'on\w+\s*=', '', query, flags=re.IGNORECASE)
        
        # Limit query length
        if len(query) > 1000:
            raise ValueError("Query too long. Maximum 1000 characters allowed.")
        
        return query.strip()
    
    def _run(self, query: str, include_private: bool = False, top_k: int = 5, user_id: str = None) -> str:
        """Search documents using secure RAG implementation"""
        try:
            # Validate and sanitize query
            sanitized_query = self._validate_query(query)
            
            # Validate top_k parameter
            top_k = min(max(1, top_k), 20)
            
            # Use stored user_id if not provided in method call
            effective_user_id = user_id if user_id is not None else self.user_id
            
            # Search for similar documents with access control
            similar_docs = self.embedding_service.search_similar(
                query=sanitized_query, 
                top_k=top_k, 
                include_private=include_private,
                user_id=effective_user_id
            )
            
            if not similar_docs:
                return "No documents found matching the query."
            
            # Format results securely
            results_summary = []
            for doc in similar_docs:
                # Only include safe information
                result_info = {
                    'id': doc['id'],
                    'content_preview': doc['content_preview'],
                    'similarity_score': doc['similarity_score'],
                    'is_private': doc['is_private'],
                    'author': doc['author'],
                    'created_at': doc['created_at']
                }
                results_summary.append(result_info)
            
            # Return formatted results without exposing full content
            summary = f"Found {len(results_summary)} relevant documents:\n\n"
            for i, doc in enumerate(results_summary, 1):
                summary += f"{i}. **{doc['author']}** ({doc['created_at']})\n"
                summary += f"   Similarity: {doc['similarity_score']:.3f}\n"
                summary += f"   Preview: {doc['content_preview']}\n"
                if doc['is_private']:
                    summary += f"   [Private Document]\n"
                summary += "\n"
            
            return summary
            
        except Exception as e:
            return f"Error in document search: {str(e)}"
    
    async def _arun(self, query: str, include_private: bool = False, top_k: int = 5, user_id: str = None) -> str:
        """Async version"""
        return self._run(query, include_private, top_k, user_id)
