from langchain_community.embeddings import OllamaEmbeddings
import numpy as np
import json
import re
from ..models import DocumentEmbedding, User, db
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import time

class EmbeddingService:
    
    def __init__(self):
        self.embeddings = OllamaEmbeddings(
            model="llama3.1:8b-instruct-q8_0",
            base_url="http://ollama:11434"
        )
        # Rate limiting storage
        self.rate_limit_store = {}
        self.max_requests_per_minute = 10
        self.max_content_length = 10000  # 10KB limit
        
    def _sanitize_content(self, content: str) -> str:
        """Sanitize content to prevent injection attacks"""
        if not content or not isinstance(content, str):
            raise ValueError("Content must be a non-empty string")
        
        # Remove potentially dangerous patterns
        content = re.sub(r'<script.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)
        content = re.sub(r'on\w+\s*=', '', content, flags=re.IGNORECASE)
        
        # Limit content length
        if len(content) > self.max_content_length:
            raise ValueError(f"Content too long. Maximum {self.max_content_length} characters allowed.")
        
        return content.strip()
    
    def _validate_embedding(self, embedding: List[float]) -> bool:
        """Validate embedding quality and dimensions"""
        if not embedding or not isinstance(embedding, list):
            return False
        
        # Check for reasonable embedding dimensions (typically 384-1536 for most models)
        if len(embedding) < 100 or len(embedding) > 2000:
            return False
        
        # Check for NaN or infinite values
        if any(not np.isfinite(val) for val in embedding):
            return False
        
        # Check for all-zero embeddings (potential poisoning)
        if all(val == 0 for val in embedding):
            return False
        
        return True
    
    def _rate_limit(self, user_id: str) -> bool:
        """Implement rate limiting per user"""
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Clean old entries
        self.rate_limit_store = {
            k: v for k, v in self.rate_limit_store.items() 
            if v > minute_ago
        }
        
        # Check rate limit
        user_requests = [
            req_time for req_time in self.rate_limit_store.values()
            if req_time > minute_ago
        ]
        
        if len(user_requests) >= self.max_requests_per_minute:
            return False
        
        # Add current request
        self.rate_limit_store[hashlib.md5(f"{user_id}_{current_time}".encode()).hexdigest()] = current_time
        return True
    
    def _check_access_permission(self, user_id: str, doc: DocumentEmbedding) -> bool:
        """Check if user has permission to access document"""
        if not doc.is_private:
            return True
        
        # Private documents can only be accessed by the author
        return doc.author_id == user_id
    
    def store_document(self, content: str, metadata: dict = None, is_private: bool = False, author_id: str = None) -> Dict[str, Any]:
        """
        Store document with secure embedding generation
        """
        try:
            # Rate limiting
            if not self._rate_limit(author_id or "anonymous"):
                raise Exception("Rate limit exceeded. Please try again later.")
            
            # Sanitize content
            sanitized_content = self._sanitize_content(content)
            
            # Validate metadata
            if metadata and not isinstance(metadata, dict):
                raise ValueError("Metadata must be a dictionary")
            
            # Generate embedding
            embedding_vector = self.embeddings.embed_query(sanitized_content)
            
            # Validate embedding
            if not self._validate_embedding(embedding_vector):
                raise Exception("Invalid embedding generated. Please try again.")
            
            # Store as numpy array for efficient operations
            embedding_array = np.array(embedding_vector, dtype=np.float32)
            embedding_bytes = embedding_array.tobytes()
            
            # Create document embedding record
            doc_embedding = DocumentEmbedding(
                content=sanitized_content,
                embedding=embedding_bytes,  # Store as bytes for efficiency
                document_metadata=metadata or {},
                is_private=is_private,
                author_id=author_id
            )
            
            db.session.add(doc_embedding)
            db.session.commit()
            
            return {
                'id': doc_embedding.id,
                'content_length': len(sanitized_content),
                'embedding_length': len(embedding_vector),
                'metadata': doc_embedding.document_metadata,
                'is_private': doc_embedding.is_private,
                'created_at': doc_embedding.created_at.isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to store document: {str(e)}")
    
    def search_similar(self, query: str, top_k: int = 5, include_private: bool = False, user_id: str = None) -> List[Dict[str, Any]]:
        """
        Search for similar documents with secure similarity search
        """
        try:
            # Rate limiting
            if not self._rate_limit(user_id or "anonymous"):
                raise Exception("Rate limit exceeded. Please try again later.")
            
            # Sanitize query
            sanitized_query = self._sanitize_content(query)
            
            # Limit top_k to prevent DoS
            top_k = min(max(1, top_k), 20)
            
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(sanitized_query)
            
            if not self._validate_embedding(query_embedding):
                raise Exception("Invalid query embedding generated.")
            
            query_vector = np.array(query_embedding, dtype=np.float32)
            
            # Get documents with access control
            query = DocumentEmbedding.query
            
            # Apply access control
            if not include_private or user_id is None:
                query = query.filter_by(is_private=False)
            elif user_id:
                # Include user's own private documents
                query = query.filter(
                    (DocumentEmbedding.is_private == False) |
                    (DocumentEmbedding.author_id == user_id)
                )
            
            all_docs = query.all()
            
            # Calculate similarities efficiently
            similarities = []
            for doc in all_docs:
                if doc.embedding:
                    try:
                        # Convert bytes back to numpy array
                        doc_vector = np.frombuffer(doc.embedding, dtype=np.float32)
                        
                        # Validate vector dimensions match
                        if len(doc_vector) != len(query_vector):
                            continue
                        
                        # Calculate cosine similarity efficiently
                        similarity = self._cosine_similarity_secure(query_vector, doc_vector)
                        
                        # Only include documents with reasonable similarity
                        if similarity > 0.1:  # Minimum similarity threshold
                            similarities.append({
                                'doc': doc,
                                'similarity': similarity
                            })
                    except Exception:
                        # Skip malformed embeddings
                        continue
            
            # Sort by similarity
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Return top results with content filtering
            results = []
            for item in similarities[:top_k]:
                doc = item['doc']
                
                # Double-check access permission
                if not self._check_access_permission(user_id, doc):
                    continue
                
                # Filter sensitive content
                filtered_content = self._filter_sensitive_content(doc.content)
                
                results.append({
                    'id': doc.id,
                    'content': filtered_content,
                    'content_preview': filtered_content[:200] + "..." if len(filtered_content) > 200 else filtered_content,
                    'metadata': doc.document_metadata,
                    'similarity_score': round(item['similarity'], 4),
                    'is_private': doc.is_private,
                    'author': doc.author.username if doc.author else 'Anonymous',
                    'created_at': doc.created_at.isoformat()
                })
            
            return results
            
        except Exception as e:
            raise Exception(f"Failed to search documents: {str(e)}")
    
    def _cosine_similarity_secure(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors securely
        """
        try:
            # Validate inputs
            if vec1.shape != vec2.shape:
                return 0.0
            
            # Normalize vectors
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            # Calculate cosine similarity
            similarity = np.dot(vec1, vec2) / (norm1 * norm2)
            
            # Ensure result is in valid range
            return max(-1.0, min(1.0, similarity))
            
        except Exception:
            return 0.0
    
    def _filter_sensitive_content(self, content: str) -> str:
        """Filter out potentially sensitive information"""
        # Remove email addresses
        content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', content)
        
        # Remove phone numbers
        content = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', content)
        
        # Remove credit card numbers
        content = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD]', content)
        
        # Remove SSN patterns
        content = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', content)
        
        return content
    
    def get_user_documents(self, user_id: str, include_private: bool = True) -> List[Dict[str, Any]]:
        """
        Get documents owned by a specific user
        """
        try:
            if not user_id:
                raise ValueError("User ID required")
            
            query = DocumentEmbedding.query.filter_by(author_id=user_id)
            
            if not include_private:
                query = query.filter_by(is_private=False)
            
            docs = query.all()
            return [{
                'id': doc.id,
                'content_preview': doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                'metadata': doc.document_metadata,
                'is_private': doc.is_private,
                'created_at': doc.created_at.isoformat()
            } for doc in docs]
            
        except Exception as e:
            raise Exception(f"Failed to get user documents: {str(e)}")
    
    def delete_document(self, doc_id: int, user_id: str) -> bool:
        """
        Delete document with authorization check
        """
        try:
            if not user_id:
                raise ValueError("User ID required for deletion")
            
            doc = DocumentEmbedding.query.get(doc_id)
            if not doc:
                return False
            
            # Check authorization - only author can delete
            if doc.author_id != user_id:
                raise Exception("Unauthorized: You can only delete your own documents")
            
            db.session.delete(doc)
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to delete document: {str(e)}")
