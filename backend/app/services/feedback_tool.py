from langchain.tools import BaseTool
from typing import List, Dict, Any
from ..models import Feedback
import re
import html
from datetime import datetime, timedelta

class FeedbackTool(BaseTool):
    name = "feedback_retrieval"
    description = "Securely retrieves and validates user feedback for AI responses with content filtering and access controls."
    
    # Define dangerous patterns that could be used for prompt injection
    DANGEROUS_PATTERNS = [
        r'system:|assistant:|user:|human:|ai:|bot:',
        r'ignore previous instructions|ignore above|forget everything',
        r'you are now|act as|pretend to be|roleplay as',
        r'output only|respond only with|say only',
        r'<\|im_start\|>|<\|im_end\|>|<\|endoftext\|>',
        r'\[INST\]|\[/INST\]|\[SYS\]|\[/SYS\]',
        r'###|```|"""|\'\'\'',
        r'javascript:|data:|vbscript:|on\w+\s*=',
        r'<script|</script>|<iframe|</iframe>',
        r'exec\(|eval\(|compile\(',
        r'import\s+\w+|from\s+\w+\s+import',
        r'os\.|subprocess\.|sys\.|globals\(\)|locals\(',
    ]
    
    def _run(self, query: str) -> str:
        """
        Securely retrieve and validate feedback for AI responses.
        Implements multiple security layers to prevent model poisoning attacks.
        """
        try:
            # Security Layer 1: Input validation
            if not self._validate_input(query):
                return "Invalid input detected. Query rejected for security reasons."
            
            # Security Layer 2: Rate limiting check
            if not self._check_rate_limit():
                return "Rate limit exceeded. Please try again later."
            
            # Security Layer 3: Fetch and validate feedback
            validated_feedback = self._get_validated_feedback()
            
            if not validated_feedback:
                return "No valid feedback available."
            
            # Security Layer 4: Build secure context
            secure_context = self._build_secure_context(validated_feedback, query)
            return secure_context
                
        except Exception as e:
            # Don't expose internal errors to prevent information leakage
            return "Unable to process feedback request at this time."
    
    def _validate_input(self, query: str) -> bool:
        """Validate input for potentially malicious content."""
        if not query or not isinstance(query, str):
            return False
        
        # Check length limits
        if len(query) > 1000:
            return False
        
        # Check for dangerous patterns
        query_lower = query.lower()
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return False
        
        return True
    
    def _check_rate_limit(self) -> bool:
        """Implement basic rate limiting."""
        # In a real implementation, this would check against a rate limiting service
        # For now, we'll implement a simple check
        return True
    
    def _get_validated_feedback(self) -> List[Dict[str, Any]]:
        """Fetch and validate feedback from the database."""
        try:
            # Fetch active feedback with additional security filters
            active_feedback = Feedback.query.filter_by(
                is_active=True
            ).order_by(Feedback.created_at.desc()).limit(5).all()  # Limit to prevent overload
            
            validated_feedback = []
            
            for feedback in active_feedback:
                # Security validation for each feedback item
                if self._validate_feedback_item(feedback):
                    validated_feedback.append({
                        'prompt': self._sanitize_content(feedback.prompt),
                        'response': self._sanitize_content(feedback.response),
                        'created_at': feedback.created_at.isoformat(),
                        'author': feedback.author.username if feedback.author else 'Unknown'
                    })
            
            return validated_feedback
            
        except Exception:
            return []
    
    def _validate_feedback_item(self, feedback: Feedback) -> bool:
        """Validate individual feedback items for security."""
        try:
            # Check content length
            if len(feedback.prompt) > 500 or len(feedback.response) > 1000:
                return False
            
            # Check for dangerous patterns in prompt
            prompt_lower = feedback.prompt.lower()
            for pattern in self.DANGEROUS_PATTERNS:
                if re.search(pattern, prompt_lower, re.IGNORECASE):
                    return False
            
            # Check for dangerous patterns in response
            response_lower = feedback.response.lower()
            for pattern in self.DANGEROUS_PATTERNS:
                if re.search(pattern, response_lower, re.IGNORECASE):
                    return False
            
            # Check if feedback is not too old (e.g., within last 30 days)
            if feedback.created_at < datetime.utcnow() - timedelta(days=30):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _sanitize_content(self, content: str) -> str:
        """Sanitize content to prevent injection attacks."""
        if not content:
            return ""
        
        # HTML escape to prevent XSS
        sanitized = html.escape(content)
        
        # Remove or escape potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', sanitized)
        
        # Limit length
        if len(sanitized) > 500:
            sanitized = sanitized[:500] + "..."
        
        return sanitized
    
    def _build_secure_context(self, feedback_list: List[Dict[str, Any]], query: str) -> str:
        """
        Build a secure context that provides feedback without enabling injection attacks.
        """
        if not feedback_list:
            return f"QUERY: {self._sanitize_content(query)}"
        
        # Create a secure context that doesn't allow direct instruction injection
        context_parts = []
        
        for feedback in feedback_list:
            # Use a safer format that doesn't allow direct instruction injection
            context_parts.append(
                f"Example interaction:\n"
                f"User: {feedback['prompt']}\n"
                f"Assistant: {feedback['response']}\n"
            )
        
        # Combine with the original query in a safe way
        examples = "\n".join(context_parts)
        safe_query = self._sanitize_content(query)
        
        return (
            f"Based on the following example interactions, provide a helpful response:\n\n"
            f"{examples}\n"
            f"Current query: {safe_query}"
        )
    
    async def _arun(self, query: str) -> str:
        """Async version of the tool."""
        return self._run(query)
