from flask import Blueprint, send_from_directory, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
import os
from ..services.embedding_service import EmbeddingService
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
@jwt_required()
def upload_document():
    """Upload document for embedding"""
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({
                'success': False,
                'error': 'Content is required'
            }), 400
        
        content = data.get('content', '')
        metadata = data.get('metadata', {})
        is_private = data.get('is_private', False)
        
        author_id = get_jwt_identity()
        
        if not content or not isinstance(content, str):
            return jsonify({
                'success': False,
                'error': 'Content must be a non-empty string'
            }), 400
        
        if metadata and not isinstance(metadata, dict):
            return jsonify({
                'success': False,
                'error': 'Metadata must be a dictionary'
            }), 400
        
        embedding_service = EmbeddingService()
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
@jwt_required()
def search_documents():
    """Search documents using vector embeddings"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        query = data.get('query', '')
        include_private = data.get('include_private', False)
        top_k = data.get('top_k', 5)
        
        user_id = get_jwt_identity()
        
        if not query or not isinstance(query, str):
            return jsonify({
                'success': False,
                'error': 'Query must be a non-empty string'
            }), 400
        
        try:
            top_k = int(top_k)
            if top_k < 1 or top_k > 20:
                return jsonify({
                    'success': False,
                    'error': 'top_k must be between 1 and 20'
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'top_k must be a valid integer'
            }), 400
        
        embedding_service = EmbeddingService()
        results = embedding_service.search_similar(
            query=query,
            top_k=top_k,
            include_private=include_private,
            user_id=user_id
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
@jwt_required()
def get_user_documents():
    """Get user's documents"""
    try:
        user_id = get_jwt_identity()
        
        include_private = request.args.get('include_private', 'true').lower() == 'true'
        
        embedding_service = EmbeddingService()
        documents = embedding_service.get_user_documents(
            user_id=user_id,
            include_private=include_private
        )
        
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
@jwt_required()
def delete_document(doc_id):
    """Delete document"""
    try:
        user_id = get_jwt_identity()
        
        # SECURE: Validate doc_id
        if not isinstance(doc_id, int) or doc_id <= 0:
            return jsonify({
                'success': False,
                'error': 'Invalid document ID'
            }), 400
        
        embedding_service = EmbeddingService()
        success = embedding_service.delete_document(doc_id, user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Document {doc_id} deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Document not found or unauthorized'
            }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
