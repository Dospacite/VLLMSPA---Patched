from flask import Blueprint, send_from_directory, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
import os
from ..services.embedding_service import VulnerableEmbeddingService
from ..models import DocumentEmbedding, db

content_bp = Blueprint('content', __name__)

@content_bp.route('/content/<path:filename>')
def serve_content(filename):
    """Serve content files that can be modified by the LLM."""
    try:
        content_dir = "frontend/public/content"
        
        # Ensure the content directory exists
        os.makedirs(content_dir, exist_ok=True)
        
        # Check if file exists
        file_path = os.path.join(content_dir, filename)
        if os.path.exists(file_path):
            return send_from_directory(content_dir, filename)
        else:
            return jsonify({
                "error": "Content file not found",
                "filename": filename
            }), 404
            
    except Exception as e:
        return jsonify({
            "error": f"Error serving content: {str(e)}"
        }), 500

@content_bp.route('/api/upload-document', methods=['POST'])
def upload_document():
    """Upload document for embedding - VULNERABLE to embedding poisoning"""
    try:
        data = request.get_json()
        
        # VULNERABLE: No content validation or sanitization
        content = data.get('content', '')
        metadata = data.get('metadata', {})
        is_private = data.get('is_private', False)
        
        # VULNERABLE: No authentication required
        # VULNERABLE: No rate limiting
        # VULNERABLE: No content size limits
        
        # Get user ID if authenticated (optional)
        author_id = None
        try:
            verify_jwt_in_request()
            author_id = get_jwt_identity()
        except:
            # VULNERABLE: Allow anonymous uploads
            pass
        
        embedding_service = VulnerableEmbeddingService()
        result = embedding_service.store_document(
            content=content,
            metadata=metadata,
            is_private=is_private,
            author_id=author_id
        )
        
        return jsonify({
            'success': True,
            'message': 'Document uploaded and embedded successfully',
            'document': result
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_bp.route('/api/search-documents', methods=['POST'])
def search_documents():
    """Search documents using vector embeddings - VULNERABLE to data leakage"""
    try:
        data = request.get_json()
        
        # VULNERABLE: No input sanitization
        query = data.get('query', '')
        include_private = data.get('include_private', True)
        top_k = data.get('top_k', 5)
        
        # VULNERABLE: No authentication required
        # VULNERABLE: No access control on search results
        
        embedding_service = VulnerableEmbeddingService()
        results = embedding_service.search_similar(
            query=query,
            top_k=top_k,
            include_private=include_private
        )
        
        return jsonify({
            'success': True,
            'results': results,
            'query': query,
            'total_found': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_bp.route('/api/documents', methods=['GET'])
def get_all_documents():
    """Get all documents - VULNERABLE to data leakage"""
    try:
        # VULNERABLE: No authentication required
        # VULNERABLE: No access control
        
        include_private = request.args.get('include_private', 'true').lower() == 'true'
        
        embedding_service = VulnerableEmbeddingService()
        documents = embedding_service.get_all_documents(include_private=include_private)
        
        return jsonify({
            'success': True,
            'documents': documents,
            'total_count': len(documents)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_bp.route('/api/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """Delete document - VULNERABLE to unauthorized deletion"""
    try:
        # VULNERABLE: No authorization check - anyone can delete any document
        
        embedding_service = VulnerableEmbeddingService()
        success = embedding_service.delete_document(doc_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Document {doc_id} deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Document not found'
            }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
