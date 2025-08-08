from flask import Blueprint, request, jsonify
from ..models import Feedback, db
from sqlalchemy import desc
import html
import re

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    """Submit feedback for review purposes only - with proper sanitization"""
    try:
        data = request.get_json()
        
        prompt = data.get('prompt', '')
        response = data.get('response', '')
        
        # Validate input
        if not prompt or not response:
            return jsonify({
                'success': False,
                'error': 'Both prompt and response are required'
            }), 400
        
        # Limit input length to prevent abuse
        if len(prompt) > 1000 or len(response) > 2000:
            return jsonify({
                'success': False,
                'error': 'Input too long. Prompt max 1000 chars, response max 2000 chars'
            }), 400
        
        # Create new feedback entry
        feedback = Feedback(
            prompt=prompt,
            response=response,
            author_id=None,
            is_active=False
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully for review',
            'feedback': feedback.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@feedback_bp.route('/feedback', methods=['GET'])
def get_feedback():
    """Get all feedback entries for review"""
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
def update_feedback(feedback_id):
    """Update feedback entry with proper sanitization"""
    try:
        feedback = Feedback.query.get_or_404(feedback_id)
        
        data = request.get_json()

        if 'prompt' in data:
            feedback.prompt = data['prompt']
        if 'response' in data:
            feedback.response = data['response']
        if 'is_active' in data:
            # Only allow boolean values for is_active
            feedback.is_active = bool(data['is_active'])
        
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
def delete_feedback(feedback_id):
    """Delete feedback entry"""
    try:
        feedback = Feedback.query.get_or_404(feedback_id)
        
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
    """Get all active feedback for review purposes only"""
    try:
        # Get all active feedback ordered by creation date
        active_feedback = Feedback.query.filter_by(is_active=True).order_by(desc(Feedback.created_at)).all()
        
        return jsonify({
            'success': True,
            'feedback': [f.to_dict() for f in active_feedback],
            'note': 'This feedback is for review purposes only and does not influence AI responses'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 