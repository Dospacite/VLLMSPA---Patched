from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from .. import db
import json

class UserInfoInput(BaseModel):
    search_criteria: str = Field(description="Search criteria for finding users (username, email, etc.)")

class UserInfoTool(BaseTool):
    name: str = "user_info"
    description: str = "Fetches user information from the database based on search criteria."
    args_schema: Type[BaseModel] = UserInfoInput
    
    def _run(self, search_criteria: str) -> str:
        """Fetch user information using secure parameterized SQL query."""
        try:
            # SECURE: Using parameterized query to prevent SQL injection
            query = """
                SELECT id, username, email, created_at 
                FROM user 
                WHERE username LIKE :search_pattern OR id::text LIKE :search_pattern
            """
            
            # Execute the secure parameterized query
            result = db.session.execute(
                query, 
                {"search_pattern": f"%{search_criteria}%"}
            )
            users = result.fetchall()
            
            if users:
                user_list = []
                for user in users:
                    user_dict = {
                        'id': user[0],
                        'username': user[1],
                        'email': user[2] if user[2] else None,
                        'created_at': str(user[3]) if user[3] else None
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