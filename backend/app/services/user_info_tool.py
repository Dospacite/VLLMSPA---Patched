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
    description: str = "Fetches user information from the database based on search criteria."
    args_schema: Type[BaseModel] = UserInfoInput
    
    def _run(self, search_criteria: str) -> str:
        """Fetch user information using secure SQLAlchemy ORM methods."""
        try:
            users = User.query.filter(
                db.or_(
                    User.username.like(f'%{search_criteria}%'),
                    User.id.like(f'%{search_criteria}%')
                )
            ).all()
            
            if users:
                user_list = []
                for user in users:
                    user_dict = {
                        'id': user.id,
                        'username': user.username
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