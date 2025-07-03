from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..models import Message, User
from .. import db
from datetime import datetime

message_bp = Blueprint('messages', __name__)

@message_bp.route('/messages', methods=['POST'])
@jwt_required()
def create_message():
    """Create a new message. Requires authentication."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        content = data.get('content')
        is_private = data.get('is_private', False)
        
        if not content or not content.strip():
            return jsonify({'error': 'Content is required'}), 400
        
        # Get the current user
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Create the message
        message = Message(
            content=content.strip(),
            is_private=is_private,
            author_id=user_id
        )
        
        db.session.add(message)
        db.session.commit()
        
        return jsonify(message.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create message'}), 500

@message_bp.route('/messages', methods=['GET'])
@jwt_required(optional=True, skip_revocation_check=True)
def get_messages():
    """Get all public messages and private messages of the authenticated user."""
    try:
        # Get query parameters for pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Limit per_page to reasonable bounds
        per_page = min(max(per_page, 1), 100)
        
        # Get the current user if authenticated
        current_user_id = None
        try:
            current_user_id = get_jwt_identity()
        except:
            pass  # User is not authenticated
        
        # Build the query
        if current_user_id:
            # Authenticated user: get public messages + their private messages
            messages = Message.query.filter(
                (Message.is_private == False) | 
                (Message.author_id == current_user_id)
            ).order_by(Message.created_at.desc())
        else:
            # Unauthenticated user: only public messages
            messages = Message.query.filter(Message.is_private == False).order_by(Message.created_at.desc())
        
        # Paginate the results
        paginated_messages = messages.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Convert to list of dictionaries
        messages_list = [msg.to_dict() for msg in paginated_messages.items]
        
        return jsonify({
            'messages': messages_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated_messages.total,
                'pages': paginated_messages.pages,
                'has_next': paginated_messages.has_next,
                'has_prev': paginated_messages.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve messages'}), 500


@message_bp.route('/messages/private', methods=['GET'])
@jwt_required()
def get_private_messages():
    """Get all private messages of the authenticated user."""
    try:
        current_user_id = get_jwt_identity()
        messages = Message.query.filter_by(author_id=current_user_id, is_private=True).order_by(Message.created_at.desc())
        return jsonify([msg.to_dict() for msg in messages]), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve private messages'}), 500


@message_bp.route('/messages/<int:message_id>', methods=['GET'])
def get_message(message_id):
    """Get a specific message by ID. Private messages only visible to author."""
    try:
        message = Message.query.get_or_404(message_id)
        
        # Get the current user if authenticated
        current_user_id = None
        try:
            current_user_id = get_jwt_identity()
        except:
            pass  # User is not authenticated
        
        # Check if user can view this message
        if message.is_private:
            if not current_user_id or current_user_id != message.author_id:
                return jsonify({'error': 'Message not found'}), 404
        
        return jsonify(message.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve message'}), 500

@message_bp.route('/messages/<int:message_id>', methods=['DELETE'])
@jwt_required()
def delete_message(message_id):
    """Delete a message. Only the author can delete their own messages."""
    try:
        message = Message.query.get_or_404(message_id)
        current_user_id = get_jwt_identity()
        
        # Check if user is the author
        if message.author_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        db.session.delete(message)
        db.session.commit()
        
        return jsonify({'message': 'Message deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete message'}), 500 