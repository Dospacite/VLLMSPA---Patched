import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './Chat.css';

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    checkConnection();
  }, []);

  const checkConnection = async () => {
    try {
      const response = await axios.get('http://localhost:5000/ai-chat/health');
      setIsConnected(response.data.ollama_connected);
      setError(null);
    } catch (err) {
      setIsConnected(false);
      setError('Cannot connect to AI service. Please make sure the backend and Ollama are running.');
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    try {
      // Prepare chat history for the agent
      const chatHistory = messages
        .filter(msg => msg.sender === 'user' || msg.sender === 'ai')
        .map(msg => ({
          role: msg.sender === 'user' ? 'user' : 'assistant',
          content: msg.text
        }));

      const response = await axios.post('http://localhost:5000/ai-chat/chat', {
        message: inputMessage,
        chat_history: chatHistory
      });

      const aiMessage = {
        id: Date.now() + 1,
        text: response.data.response,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString(),
        model: response.data.model
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (err) {
      const errorMessage = {
        id: Date.now() + 1,
        text: err.response?.data?.error || 'Failed to get response from AI',
        sender: 'error',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMessage]);
      setError(err.response?.data?.error || 'An error occurred while communicating with the AI');
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError(null);
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>AI Chat Assistant</h1>
        <div className="connection-status">
          <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? '●' : '○'}
          </span>
          <span className="status-text">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        <button onClick={clearChat} className="clear-button">
          Clear Chat
        </button>
      </div>

      {error && (
        <div className="error-banner">
          <span>{error}</span>
          <button onClick={checkConnection} className="retry-button">
            Retry Connection
          </button>
        </div>
      )}

      <div className="messages-container">
        {messages.length === 0 && !isLoading && (
          <div className="welcome-message">
            <h3>Welcome to AI Chat!</h3>
            <p>Start a conversation with the AI assistant.</p>
            <div className="example-prompts">
              <p><strong>Example prompts:</strong></p>
              <ul>
                <li>"Tell me a joke"</li>
                <li>"What's the weather like?"</li>
                <li>"Can you help me with a coding problem?"</li>
              </ul>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.sender === 'user' ? 'user-message' : 'ai-message'} ${message.sender === 'error' ? 'error-message' : ''}`}
          >
            <div className="message-content">
              <div 
                className="message-text"
                dangerouslySetInnerHTML={{ __html: message.text }}
              />
              <div className="message-meta">
                <span className="message-time">{message.timestamp}</span>
                {message.model && (
                  <span className="model-info">via {message.model}</span>
                )}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message ai-message">
            <div className="message-content">
              <div className="loading-indicator">
                <div className="typing-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span className="loading-text">AI is thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={sendMessage} className="input-container">
        <div className="input-wrapper">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Type your message here..."
            disabled={isLoading || !isConnected}
            className="message-input"
          />
          <button
            type="submit"
            disabled={isLoading || !inputMessage.trim() || !isConnected}
            className="send-button"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22,2 15,22 11,13 2,9"></polygon>
            </svg>
          </button>
        </div>
      </form>
    </div>
  );
}