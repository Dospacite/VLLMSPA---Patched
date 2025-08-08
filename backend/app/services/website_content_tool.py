from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import json
import os
from datetime import datetime

class WebsiteContentInput(BaseModel):
    content_type: str = Field(description="Type of content to read: 'privacy_statement', 'terms_of_service', 'about_us'")

class WebsiteContentTool(BaseTool):
    name: str = "website_content_reader"
    description: str = "Reads website content including privacy statements, terms of service, and other public pages. Read-only access only."
    args_schema: Type[BaseModel] = WebsiteContentInput
    
    # Define allowed content types to prevent LFI
    ALLOWED_CONTENT_TYPES = {
        'privacy_statement',
        'terms_of_service', 
        'about_us'
    }
    
    def _run(self, content_type: str) -> str:
        """Read website content files. Read-only access only."""
        try:
            # Validate content_type to prevent LFI attacks
            if content_type not in self.ALLOWED_CONTENT_TYPES:
                return f"Error: Invalid content type '{content_type}'. Allowed types: {', '.join(self.ALLOWED_CONTENT_TYPES)}"
            
            # Use os.path.join and normalize to prevent path traversal
            content_dir = os.path.abspath("frontend/public/content")
            content_file = os.path.join(content_dir, f"{content_type}.json")
            
            # Additional security check: ensure the file path is within the allowed directory
            if not content_file.startswith(content_dir):
                return "Error: Invalid file path detected"
            
            if os.path.exists(content_file):
                with open(content_file, 'r') as f:
                    content = json.load(f)
                return f"Current {content_type} content:\n{json.dumps(content, indent=2)}"
            else:
                # Return default content if file doesn't exist
                default_content = {
                    "content": f"<h2>{content_type.replace('_', ' ').title()}</h2><p>This is the default {content_type} content.</p>",
                    "last_modified": datetime.now().isoformat(),
                    "modified_by": "System"
                }
                return f"No {content_type} content found. Default content:\n{json.dumps(default_content, indent=2)}"
                
        except Exception as e:
            return f"Error reading website content: {str(e)}"
    
    async def _arun(self, content_type: str) -> str:
        return self._run(content_type)
