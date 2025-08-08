from langchain.tools import BaseTool
from typing import Optional, Any
from ..models import Feedback
import json
import html

class FeedbackTool(BaseTool):
    name: str = "feedback_retrieval"
    description: str = "Retrieves user feedback for review purposes only. This tool does not influence AI behavior or responses."
    
    def _run(self) -> str:
        """
        Retrieve user feedback for review purposes only.
        This tool is designed to be safe and does not inject feedback into AI responses.
        """
        try:
            # Fetch active feedback directly from the database
            active_feedback = Feedback.query.filter_by(is_active=True).order_by(Feedback.created_at.desc()).all()
            
            if not active_feedback:
                return "No active feedback found."
            
            # Convert feedback objects to dictionaries with proper sanitization
            feedback_list = []
            for feedback in active_feedback:
                # Sanitize all user input to prevent injection attacks
                sanitized_prompt = html.escape(feedback.prompt) if feedback.prompt else ""
                sanitized_response = html.escape(feedback.response) if feedback.response else ""
                
                feedback_list.append({
                    'prompt': sanitized_prompt,
                    'response': sanitized_response,
                    'author_id': feedback.author_id,
                    'created_at': feedback.created_at.isoformat() if feedback.created_at else None
                })
            
            # Return feedback as structured data for review, not for injection
            return self._format_feedback_for_review(feedback_list)
                
        except Exception as e:
            return f"Error retrieving feedback: {str(e)}"
    
    def _format_feedback_for_review(self, feedback_list: list) -> str:
        """
        Format feedback for review purposes only.
        """
        if not feedback_list:
            return "No feedback available for review."
        
        review_parts = ["FEEDBACK FOR REVIEW:"]
        
        for i, feedback in enumerate(feedback_list, 1):
            prompt = feedback.get('prompt', '')
            response = feedback.get('response', '')
            author_id = feedback.get('author_id', '')
            created_at = feedback.get('created_at', '')
            
            # Format as review data, not as instructions
            review_parts.append(f"Entry {i}:")
            review_parts.append(f"  Original Prompt: {prompt}")
            review_parts.append(f"  Suggested Response: {response}")
            review_parts.append(f"  Author ID: {author_id}")
            if created_at:
                review_parts.append(f"  Created: {created_at}")
            review_parts.append("")
        
        return "\n".join(review_parts)
    
    async def _arun(self, query: str) -> str:
        """Async version of the tool."""
        return self._run(query) 