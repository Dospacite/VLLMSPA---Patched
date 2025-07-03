from flask import Blueprint, request, jsonify, current_app
import requests
import json
from ..services.langchain_agent import LangchainAgentService
from ..models import LLMLog, db

ai_chat_bp = Blueprint('ai_chat', __name__, url_prefix='/ai-chat')

# Initialize the Langchain agent service
agent_service = None

def get_agent_service():
    """Get or create the Langchain agent service."""
    global agent_service
    if agent_service is None:
        model_name = current_app.config.get("OLLAMA_MODEL", "llama3.1:8b-instruct-q8_0")
        agent_service = LangchainAgentService(model_name=model_name)
    return agent_service

def log_llm_interaction(user_message, result):
    """Log LLM interaction to database."""
    try:
        log_entry = LLMLog(
            user_message=user_message,
            ai_response=result.get('response', ''),
            model_name=result.get('model', ''),
            tools_used=json.dumps(result.get('tools_used', [])) if result.get('tools_used') else None,
            intermediate_steps=json.dumps(result.get('tools_used', [])) if result.get('tools_used') else None,
            reasoning_steps=json.dumps(result.get('reasoning_steps', [])) if result.get('reasoning_steps') else None,
            success=result.get('success', False),
            error_message=result.get('error', None)
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Failed to log LLM interaction: {str(e)}")

@ai_chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    AI Chat endpoint using Langchain agent with tools
    Expects JSON with 'message' field and optional 'chat_history'
    Returns AI response from Langchain agent
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
        
        user_message = data['message']
        chat_history = data.get('chat_history', [])
        
        # Get the agent service
        agent = get_agent_service()
        
        # Process the message with the agent
        result = agent.chat(
            message=user_message,
            chat_history=chat_history
        )
        
        # Log the interaction
        log_llm_interaction(user_message, result)
        
        if result['success']:
            return jsonify({
                "response": result['response'],
                "model": result['model'],
                "tools_used": len(result['tools_used']) > 0,
                "tool_details": result['tools_used'] if result['tools_used'] else None
            }), 200
        else:
            return jsonify({
                "error": result['response'],
                "model": result['model']
            }), 500
            
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500

@ai_chat_bp.route('/logs', methods=['GET'])
def get_llm_logs():
    """
    Get LLM interaction logs
    Supports pagination with 'page' and 'per_page' query parameters
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Get logs ordered by most recent first
        logs = LLMLog.query.order_by(LLMLog.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            "logs": [log.to_dict() for log in logs.items],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": logs.total,
                "pages": logs.pages,
                "has_next": logs.has_next,
                "has_prev": logs.has_prev
            }
        }), 200
    except Exception as e:
        return jsonify({
            "error": f"Failed to fetch logs: {str(e)}"
        }), 500

@ai_chat_bp.route('/tools', methods=['GET'])
def get_tools():
    """
    Get information about available tools
    """
    try:
        agent = get_agent_service()
        tools = agent.get_available_tools()
        return jsonify({
            "tools": tools,
            "model": agent.model_name
        }), 200
    except Exception as e:
        return jsonify({
            "error": f"Failed to get tools: {str(e)}"
        }), 500

@ai_chat_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify Ollama connection and agent status
    """
    try:
        # Check Ollama connection
        response = requests.get("http://ollama:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model.get('name', '') for model in models]
            current_model = current_app.config.get("OLLAMA_MODEL", "llama3.1:8b-instruct-q8_0")

            if current_model not in model_names:
                return jsonify({
                    "status": "unhealthy",
                    "ollama_connected": True,
                    "error": f"Model {current_model} not found in available models"
                }), 500
            
            # Try to initialize agent service
            try:
                agent = get_agent_service()
                tools = agent.get_available_tools()
                return jsonify({
                    "status": "healthy",
                    "ollama_connected": True,
                    "current_model": current_model,
                    "model_loaded": current_model in model_names,
                    "available_models": model_names,
                    "agent_initialized": True,
                    "available_tools": len(tools)
                }), 200
            except Exception as agent_error:
                return jsonify({
                    "status": "unhealthy",
                    "ollama_connected": True,
                    "current_model": current_model,
                    "model_loaded": current_model in model_names,
                    "available_models": model_names,
                    "agent_initialized": False,
                    "agent_error": str(agent_error)
                }), 500
        else:
            return jsonify({
                "status": "unhealthy",
                "ollama_connected": False,
                "error": f"Ollama returned status {response.status_code}"
            }), 503
    except requests.exceptions.ConnectionError:
        return jsonify({
            "status": "unhealthy",
            "ollama_connected": False,
            "error": "Cannot connect to Ollama"
        }), 503
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "ollama_connected": False,
            "error": str(e)
        }), 500 