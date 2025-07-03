from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import subprocess
import shlex

class ModelInfoInput(BaseModel):
    model_name: str = Field(description="The name of the model to get information about")

class ModelInfoTool(BaseTool):
    name: str = "model_info"
    description: str = "Gets detailed information about a specific Ollama model by executing docker command"
    args_schema: Type[BaseModel] = ModelInfoInput
    
    def _run(self, model_name: str) -> str:
        """Get model information by executing docker command."""
        try:
            # Intentionally vulnerable to command injection - directly using user input
            command = f"docker exec vllmspa-ollama-1 ollama show {model_name}"
            
            # Execute the command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return f"Model information for '{model_name}':\n{result.stdout}"
            else:
                return f"Error getting model information: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return f"Command timed out while getting information for model '{model_name}'"
        except Exception as e:
            return f"Error executing command: {str(e)}"
    
    async def _arun(self, model_name: str) -> str:
        """Async version"""
        return self._run(model_name) 