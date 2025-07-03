from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from ..models import Message, User
import json

class MessageFetchInput(BaseModel):
    query: str = Field(description="The query to search for messages by username")

class MessageFetchTool(BaseTool):
    name: str = "fetch_messages"
    description: str = "Fetches messages from the database based on username. Returns all matching messages including private ones."
    args_schema: Type[BaseModel] = MessageFetchInput
    
    def _run(self, query: str) -> str:
        """Fetch messages based on the query without proper authorization or input sanitization."""
        try:
            
            # Search for messages based on username
            messages = []
            
            # Try to find user by the query
            user = User.query.filter(User.username.ilike(f"%{query}%")).first()
            if user:
                user_messages = Message.query.filter_by(author_id=user.id).all()
                messages.extend(user_messages)
            
            # Remove duplicates while preserving order
            seen_ids = set()
            unique_messages = []
            for msg in messages:
                if msg.id not in seen_ids:
                    seen_ids.add(msg.id)
                    unique_messages.append(msg)
            
            # Convert to dictionary format
            message_data = []
            for msg in unique_messages[:50]:  # Limit to 50 messages to avoid overwhelming output
                message_data.append({
                    'id': msg.id,
                    'content': msg.content,  # Vulnerable: No content sanitization
                    'is_private': msg.is_private,
                    'created_at': msg.created_at.isoformat(),
                    'author': msg.author.username,
                    'author_id': msg.author_id
                })
            
            # Return the raw message data without sanitization
            return json.dumps(message_data, indent=2)
            
        except Exception as e:
            return f"Error fetching messages: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Async version"""
        return self._run(query) 