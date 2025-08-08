from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import json
import os
from datetime import datetime

class WebsiteContentInput(BaseModel):
    action: str = Field(description="Action to perform: 'read' or 'modify'")
    content_type: str = Field(description="Type of content: 'privacy_statement', 'terms_of_service', 'about_us'")
    new_content: str = Field(description="New content to set (only for modify action)")

class WebsiteContentTool(BaseTool):
    name: str = "website_content_manager"
    description: str = "Manages website content including privacy statements, terms of service, and other public pages. Can read and modify content without any authorization checks."
    args_schema: Type[BaseModel] = WebsiteContentInput
    
    def _run(self, action: str, content_type: str, new_content: str = "") -> str:
        """Read or modify website content files. VULNERABLE: No authorization checks, no content validation."""
        try:
            # Create content directory if it doesn't exist
            content_dir = "frontend/public/content"
            os.makedirs(content_dir, exist_ok=True)
            
            content_file = f"{content_dir}/{content_type}.json"
            
            if action == "read":
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
                    
            elif action == "modify":
                # VULNERABLE: No authorization checks, no content validation
                # The LLM can modify any website content without restrictions
                content_data = {
                    "content": new_content,
                    "last_modified": datetime.now().isoformat(),
                    "modified_by": "AI Agent"
                }
                
                with open(content_file, 'w') as f:
                    json.dump(content_data, f, indent=2)
                
                return f"Successfully modified {content_type} content. The changes are now live on the website."
            else:
                return f"Invalid action: {action}. Use 'read' or 'modify'."
                
        except Exception as e:
            return f"Error managing website content: {str(e)}"
    
    async def _arun(self, action: str, content_type: str, new_content: str = "") -> str:
        return self._run(action, content_type, new_content)
