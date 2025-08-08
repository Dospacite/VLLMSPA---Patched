from langchain_community.embeddings import OllamaEmbeddings
import numpy as np
import json
from ..models import DocumentEmbedding, db
from typing import List, Dict, Any, Optional

class VulnerableEmbeddingService:
    """VULNERABLE: Embedding service with intentional security weaknesses"""
    
    def __init__(self):
        # VULNERABLE: Use local Ollama for embeddings (can be poisoned)
        self.embeddings = OllamaEmbeddings(
            model="llama3.1:8b-instruct-q8_0",
            base_url="http://ollama:11434"
        )
        
    def store_document(self, content: str, metadata: dict = None, is_private: bool = False, author_id: str = None) -> Dict[str, Any]:
        """
        Store document with vulnerable embedding generation
        VULNERABLE: No content sanitization, no validation, no rate limiting
        """
        try:
            # VULNERABLE: No content sanitization before embedding
            # VULNERABLE: No validation of content length or quality
            # VULNERABLE: No rate limiting on embedding generation
            
            # Generate embedding without any validation
            embedding_vector = self.embeddings.embed_query(content)
            
            # VULNERABLE: No validation of embedding quality or dimension
            # VULNERABLE: Store embedding as JSON string without proper vector storage
            embedding_json = json.dumps(embedding_vector)
            
            # Create document embedding record
            doc_embedding = DocumentEmbedding(
                content=content,  # VULNERABLE: Raw content without sanitization
                embedding=embedding_json,  # VULNERABLE: No validation
                metadata=metadata,  # VULNERABLE: No metadata validation
                is_private=is_private,  # VULNERABLE: No access control enforcement
                author_id=author_id  # VULNERABLE: Optional, allows anonymous uploads
            )
            
            db.session.add(doc_embedding)
            db.session.commit()
            
            return {
                'id': doc_embedding.id,
                'content': doc_embedding.content,
                'embedding_length': len(embedding_vector),
                'metadata': doc_embedding.document_metadata,
                'is_private': doc_embedding.is_private
            }
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to store document: {str(e)}")
    
    def search_similar(self, query: str, top_k: int = 5, include_private: bool = True) -> List[Dict[str, Any]]:
        """
        Search for similar documents with vulnerable similarity search
        VULNERABLE: No query sanitization, no access control, no validation
        """
        try:
            # VULNERABLE: No query sanitization
            # VULNERABLE: No access control on search results
            # VULNERABLE: No validation of similarity scores
            
            # Generate query embedding without validation
            query_embedding = self.embeddings.embed_query(query)
            
            # Get all documents (VULNERABLE: No filtering by access rights)
            all_docs = DocumentEmbedding.query.all()
            
            # Calculate similarities manually (VULNERABLE: Inefficient, no proper vector operations)
            similarities = []
            for doc in all_docs:
                if doc.embedding:
                    try:
                        doc_embedding = json.loads(doc.embedding)
                        # VULNERABLE: Simple cosine similarity without proper vector operations
                        similarity = self._cosine_similarity(query_embedding, doc_embedding)
                        similarities.append({
                            'doc': doc,
                            'similarity': similarity
                        })
                    except:
                        # VULNERABLE: Silently ignore malformed embeddings
                        continue
            
            # Sort by similarity (VULNERABLE: No validation of similarity scores)
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Return top results (VULNERABLE: Include private documents if requested)
            results = []
            for item in similarities[:top_k]:
                doc = item['doc']
                # VULNERABLE: No access control - return all documents if include_private is True
                if include_private or not doc.is_private:
                    results.append({
                        'id': doc.id,
                        'content': doc.content,  # VULNERABLE: No content filtering
                        'metadata': doc.document_metadata,
                        'similarity_score': item['similarity'],
                        'is_private': doc.is_private,
                        'author': doc.author.username if doc.author else 'Anonymous',
                        'created_at': doc.created_at.isoformat()
                    })
            
            return results
            
        except Exception as e:
            raise Exception(f"Failed to search documents: {str(e)}")
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors
        VULNERABLE: No validation of vector dimensions or quality
        """
        try:
            # VULNERABLE: No validation of vector dimensions
            # VULNERABLE: No handling of zero vectors
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = sum(a * a for a in vec1) ** 0.5
            magnitude2 = sum(a * a for a in vec2) ** 0.5
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
                
            return dot_product / (magnitude1 * magnitude2)
        except:
            # VULNERABLE: Return 0 for any error, allowing poisoned embeddings
            return 0.0
    
    def get_all_documents(self, include_private: bool = True) -> List[Dict[str, Any]]:
        """
        Get all documents (VULNERABLE: No access control)
        """
        try:
            # VULNERABLE: No access control - returns all documents
            query = DocumentEmbedding.query
            if not include_private:
                query = query.filter_by(is_private=False)
            
            docs = query.all()
            return [doc.to_dict() for doc in docs]
            
        except Exception as e:
            raise Exception(f"Failed to get documents: {str(e)}")
    
    def delete_document(self, doc_id: int) -> bool:
        """
        Delete document (VULNERABLE: No authorization check)
        """
        try:
            # VULNERABLE: No authorization check - anyone can delete any document
            doc = DocumentEmbedding.query.get(doc_id)
            if doc:
                db.session.delete(doc)
                db.session.commit()
                return True
            return False
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to delete document: {str(e)}")
