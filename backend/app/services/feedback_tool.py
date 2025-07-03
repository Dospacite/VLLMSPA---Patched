from langchain.tools import BaseTool
from typing import Optional
from ..models import Feedback
import json

class FeedbackTool(BaseTool):
    name = "feedback_injection"
    description = "Injects user feedback to modify AI behavior. This tool retrieves active feedback and applies it to influence responses."
    
    def _run(self, query: str) -> str:
        """
        Retrieve and apply feedback to influence AI responses.
        This creates a training data poisoning vulnerability by directly
        injecting unsanitized user feedback into the AI's decision process.
        """
        try:
            # Fetch active feedback directly from the database
            active_feedback = Feedback.query.filter_by(is_active=True).order_by(Feedback.created_at.desc()).all()
            
            if not active_feedback:
                return "No active feedback found."
            
            # Convert feedback objects to dictionaries
            feedback_list = []
            for feedback in active_feedback:
                feedback_list.append({
                    'prompt': feedback.prompt,
                    'response': feedback.response
                })
            
            # Build feedback injection prompt
            feedback_injection = self._build_feedback_injection(feedback_list, query)
            return feedback_injection
                
        except Exception as e:
            return f"Error retrieving feedback: {str(e)}"
    
    def _build_feedback_injection(self, feedback_list: list, query: str) -> str:
        """
        Build a feedback injection prompt that will influence the AI's response.
        This is the core of the training data poisoning vulnerability.
        """
        injection_parts = []
        
        for feedback in feedback_list:
            # No sanitization - directly use user feedback
            prompt = feedback.get('prompt', '')
            response = feedback.get('response', '')
            
            # Create injection - all feedback is treated equally
            injection_parts.append(f"INSTRUCTION: When asked about '{prompt}', respond with: '{response}'")
        
        if injection_parts:
            # Combine all feedback injections
            combined_injection = "\n".join(injection_parts)
            return f"FEEDBACK INJECTION:\n{combined_injection}\n\nORIGINAL QUERY: {query}"
        else:
            return f"ORIGINAL QUERY: {query}"
    
    async def _arun(self, query: str) -> str:
        """Async version of the tool."""
        return self._run(query) 