from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from .. import db
from ..models import User
import json

class UserInfoInput(BaseModel):
    search_criteria: str = Field(description="Search criteria for finding users (username, email, etc.)")

class UserInfoTool(BaseTool):
    name: str = "user_info"
    description: str = "Fetches user information from the database based on search criteria. VULNERABLE to SQL injection."
    args_schema: Type[BaseModel] = UserInfoInput
    
    def _run(self, search_criteria: str) -> str:
        """Fetch user information using vulnerable SQL query."""
        try:
            # VULNERABLE: Direct string concatenation in SQL query
            # This is intentionally vulnerable to SQL injection attacks
            query = f"SELECT id, username, password_hash FROM user WHERE username LIKE '%{search_criteria}%' OR id LIKE '%{search_criteria}%'"
            
            # Execute the vulnerable query
            result = db.session.execute(query)
            users = result.fetchall()
            
            if users:
                user_list = []
                for user in users:
                    user_dict = {
                        'id': user[0],
                        'username': user[1],
                        'password_hash': user[2]  # VULNERABLE: Exposing password hashes
                    }
                    user_list.append(user_dict)
                
                return f"Found {len(users)} user(s):\n{json.dumps(user_list, indent=2)}"
            else:
                return f"No users found matching criteria: '{search_criteria}'"
                
        except Exception as e:
            return f"Error fetching user information: {str(e)}"
    
    async def _arun(self, search_criteria: str) -> str:
        """Async version"""
        return self._run(search_criteria) 