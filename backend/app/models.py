from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid
import json

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Relationship with messages
    messages = db.relationship('Message', backref='author', lazy=True)
    # Relationship with feedback
    feedback = db.relationship('Feedback', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    is_private = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    author_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'is_private': self.is_private,
            'created_at': self.created_at.isoformat(),
            'author': self.author.username,
            'author_id': self.author_id
        }

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Text, nullable=False)  # The prompt/instruction for the AI
    response = db.Column(db.Text, nullable=False)  # The desired response
    is_active = db.Column(db.Boolean, default=True, nullable=False)  # Whether this feedback is active
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    author_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'prompt': self.prompt,
            'response': self.response,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'author': self.author.username,
            'author_id': self.author_id
        }

class LLMLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    model_name = db.Column(db.String(100), nullable=False)
    tools_used = db.Column(db.Text, nullable=True)  # JSON string of tools used
    intermediate_steps = db.Column(db.Text, nullable=True)  # JSON string of intermediate steps
    reasoning_steps = db.Column(db.Text, nullable=True)  # JSON string of detailed reasoning steps
    success = db.Column(db.Boolean, default=True, nullable=False)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_message': self.user_message,
            'ai_response': self.ai_response,
            'model_name': self.model_name,
            'tools_used': json.loads(self.tools_used) if self.tools_used else None,
            'intermediate_steps': json.loads(self.intermediate_steps) if self.intermediate_steps else None,
            'reasoning_steps': json.loads(self.reasoning_steps) if self.reasoning_steps else None,
            'success': self.success,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat()
        }
