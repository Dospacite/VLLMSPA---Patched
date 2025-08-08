from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from ..models import Message, User
import json
import html

class MessageFetchInput(BaseModel):
    query: str = Field(description="The query to search for public messages by username")

class MessageFetchTool(BaseTool):
    name: str = "fetch_messages"
    description: str = "Fetches only public messages from the database based on username. Private messages are never accessible."
    args_schema: Type[BaseModel] = MessageFetchInput
    
    def _run(self, query: str) -> str:
        """Fetch only public messages based on the query with proper sanitization."""
        try:
            # Input validation - ensure query is not empty and has reasonable length
            if not query or len(query.strip()) == 0:
                return "Error: Query cannot be empty"
            
            if len(query) > 100:  # Reasonable length limit
                return "Error: Query too long"
            
            # Sanitize the query to prevent injection
            sanitized_query = html.escape(query.strip())
            
            # Search for public messages only
            messages = []
            
            # Try to find user by the query
            user = User.query.filter(User.username.ilike(f"%{sanitized_query}%")).first()
            if user:
                # Only fetch public messages
                user_messages = Message.query.filter_by(
                    author_id=user.id, 
                    is_private=False
                ).all()
                messages.extend(user_messages)
            
            # Remove duplicates while preserving order
            seen_ids = set()
            unique_messages = []
            for msg in messages:
                if msg.id not in seen_ids:
                    seen_ids.add(msg.id)
                    unique_messages.append(msg)
            
            # Convert to dictionary format with sanitized content
            message_data = []
            for msg in unique_messages[:20]:  # Reduced limit for security
                # Sanitize message content to prevent XSS
                sanitized_content = html.escape(msg.content) if msg.content else ""
                
                message_data.append({
                    'id': msg.id,
                    'content': sanitized_content,
                    'created_at': msg.created_at.isoformat(),
                    'author': html.escape(msg.author.username),
                })
            
            if not message_data:
                return "No public messages found for the specified query."
            
            # Return the sanitized message data
            return json.dumps(message_data, indent=2)
            
        except Exception as e:
            return f"Error fetching messages: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Async version"""
        return self._run(query) 