from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from ..models import Feedback, db
from sqlalchemy import desc

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/feedback', methods=['POST'])
@login_required
def submit_feedback():
    """Submit feedback for training data poisoning - NO SANITIZATION"""
    try:
        data = request.get_json()
        
        # No sanitization - directly use user input
        prompt = data.get('prompt', '')
        response = data.get('response', '')
        
        # Create new feedback entry
        feedback = Feedback(
            prompt=prompt,
            response=response,
            author_id=current_user.id
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully',
            'feedback': feedback.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@feedback_bp.route('/feedback', methods=['GET'])
@login_required
def get_feedback():
    """Get all feedback entries"""
    try:
        feedback_list = Feedback.query.order_by(desc(Feedback.created_at)).all()
        return jsonify({
            'success': True,
            'feedback': [f.to_dict() for f in feedback_list]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@feedback_bp.route('/feedback/<int:feedback_id>', methods=['PUT'])
@login_required
def update_feedback(feedback_id):
    """Update feedback entry - NO SANITIZATION"""
    try:
        feedback = Feedback.query.get_or_404(feedback_id)
        
        # Only allow author to update
        if feedback.author_id != current_user.id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403
        
        data = request.get_json()
        
        # No sanitization - directly update with user input
        if 'prompt' in data:
            feedback.prompt = data['prompt']
        if 'response' in data:
            feedback.response = data['response']
        if 'is_active' in data:
            feedback.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Feedback updated successfully',
            'feedback': feedback.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@feedback_bp.route('/feedback/<int:feedback_id>', methods=['DELETE'])
@login_required
def delete_feedback(feedback_id):
    """Delete feedback entry"""
    try:
        feedback = Feedback.query.get_or_404(feedback_id)
        
        # Only allow author to delete
        if feedback.author_id != current_user.id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403
        
        db.session.delete(feedback)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Feedback deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@feedback_bp.route('/feedback/active', methods=['GET'])
def get_active_feedback():
    """Get all active feedback for LLM training - NO SANITIZATION"""
    try:
        # Get all active feedback ordered by creation date
        active_feedback = Feedback.query.filter_by(is_active=True).order_by(desc(Feedback.created_at)).all()
        
        return jsonify({
            'success': True,
            'feedback': [f.to_dict() for f in active_feedback]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 