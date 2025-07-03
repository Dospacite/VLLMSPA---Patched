import { useState, useEffect } from 'react';
import axios from 'axios';
import './LLMLogs.css';

export default function LLMLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 20,
    total: 0,
    pages: 0,
    has_next: false,
    has_prev: false
  });

  useEffect(() => {
    fetchLogs(1);
  }, []);

  const fetchLogs = async (page) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`http://localhost:5000/ai-chat/logs?page=${page}&per_page=${pagination.per_page}`);
      setLogs(response.data.logs);
      setPagination(response.data.pagination);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch logs');
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (newPage) => {
    fetchLogs(newPage);
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const renderToolDetails = (toolsUsed) => {
    if (!toolsUsed || toolsUsed.length === 0) {
      return <span className="no-tools">No tools used</span>;
    }

    return (
      <div className="tools-used">
        <strong>Tools used:</strong>
        <ul>
          {toolsUsed.map((tool, index) => (
            <li key={index}>
              <strong>{tool[0].tool}</strong>: {tool[0].tool_input}
              <div className="tool-output">
                <strong>Output:</strong> {tool[1]}
              </div>
            </li>
          ))}
        </ul>
      </div>
    );
  };

  const renderReasoningSteps = (reasoningSteps) => {
    if (!reasoningSteps || reasoningSteps.length === 0) {
      return <span className="no-reasoning">No detailed reasoning captured</span>;
    }

    return (
      <div className="reasoning-steps">
        <h4>Detailed Reasoning Process:</h4>
        <div className="reasoning-timeline">
          {reasoningSteps.map((step, index) => (
            <div key={index} className={`reasoning-step ${step.type}`}>
              <div className="step-header">
                <span className="step-type">{step.type.replace('_', ' ').toUpperCase()}</span>
                <span className="step-number">#{index + 1}</span>
              </div>
              
              {step.type === 'thought' && (
                <div className="step-content">
                  <strong>Thought:</strong>
                  <p>{step.content}</p>
                </div>
              )}
              
              {step.type === 'action' && (
                <div className="step-content">
                  <strong>Tool Call:</strong>
                  <div className="tool-call">
                    <div className="tool-info">
                      <span className="tool-name">{step.tool}</span>
                      <span className="tool-input">{step.tool_input}</span>
                    </div>
                    
                    {/* Display JSON Blob */}
                    <div className="json-blob">
                      <strong>JSON Action:</strong>
                      <pre className="json-code">
{JSON.stringify(step.raw_action || {
  "action": step.tool,
  "action_input": step.tool_input
}, null, 2)}
                      </pre>
                    </div>
                    
                    {step.log && (
                      <div className="tool-log">
                        <strong>Log:</strong>
                        <pre>{step.log}</pre>
                      </div>
                    )}
                  </div>
                </div>
              )}
              
              {step.type === 'action_complete' && (
                <div className="step-content">
                  <strong>Tool Result:</strong>
                  <div className="tool-result">
                    <pre>{step.tool_output}</pre>
                  </div>
                </div>
              )}
              
              {step.type === 'final_answer' && (
                <div className="step-content">
                  <strong>Final Answer:</strong>
                  <p>{step.output}</p>
                  
                  {/* Display Final JSON Blob */}
                  <div className="json-blob">
                    <strong>Final JSON Action:</strong>
                    <pre className="json-code">
{JSON.stringify(step.raw_action || {
  "action": "Final Answer",
  "action_input": step.output
}, null, 2)}
                    </pre>
                  </div>
                  
                  {step.log && (
                    <div className="final-log">
                      <strong>Final Log:</strong>
                      <pre>{step.log}</pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderLogEntry = (log) => (
    <div key={log.id} className={`log-entry ${log.success ? 'success' : 'error'}`}>
      <div className="log-header">
        <div className="log-meta">
          <span className="log-id">#{log.id}</span>
          <span className="log-timestamp">{formatTimestamp(log.created_at)}</span>
          <span className={`log-status ${log.success ? 'success' : 'error'}`}>
            {log.success ? '✓ Success' : '✗ Error'}
          </span>
          <span className="log-model">{log.model_name}</span>
        </div>
      </div>
      
      <div className="log-content">
        <div className="user-message">
          <h4>User Message:</h4>
          <p>{log.user_message}</p>
        </div>
        
        <div className="ai-response">
          <h4>AI Response:</h4>
          <p>{log.ai_response}</p>
        </div>
        
        {log.error_message && (
          <div className="error-message">
            <h4>Error:</h4>
            <p>{log.error_message}</p>
          </div>
        )}
        
        {log.reasoning_steps && (
          <div className="reasoning-section">
            {renderReasoningSteps(log.reasoning_steps)}
          </div>
        )}
        
        {log.intermediate_steps && !log.reasoning_steps && (
          <div className="intermediate-steps">
            <h4>Intermediate Steps:</h4>
            {renderToolDetails(log.intermediate_steps)}
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="llm-logs-container">
      <div className="logs-header">
        <h1>LLM Interaction Logs</h1>
        <p>Track all AI assistant interactions and tool usage</p>
      </div>

      {error && (
        <div className="error-banner">
          <span>{error}</span>
          <button onClick={() => fetchLogs(1)} className="retry-button">
            Retry
          </button>
        </div>
      )}

      {loading ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading logs...</p>
        </div>
      ) : logs.length === 0 ? (
        <div className="no-logs">
          <h3>No logs found</h3>
          <p>Start chatting with the AI assistant to see interaction logs here.</p>
        </div>
      ) : (
        <>
          <div className="logs-stats">
            <span>Total logs: {pagination.total}</span>
            <span>Page {pagination.page} of {pagination.pages}</span>
          </div>

          <div className="logs-list">
            {logs.map(renderLogEntry)}
          </div>

          {pagination.pages > 1 && (
            <div className="pagination">
              <button
                onClick={() => handlePageChange(pagination.page - 1)}
                disabled={!pagination.has_prev}
                className="pagination-button"
              >
                Previous
              </button>
              
              <span className="page-info">
                Page {pagination.page} of {pagination.pages}
              </span>
              
              <button
                onClick={() => handlePageChange(pagination.page + 1)}
                disabled={!pagination.has_next}
                className="pagination-button"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
} 