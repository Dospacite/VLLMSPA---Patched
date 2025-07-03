import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './Feedback.css';

const Feedback = () => {
  const { isAuthenticated, token } = useAuth();
  const [feedbackList, setFeedbackList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  
  // Form state - NO SANITIZATION
  const [formData, setFormData] = useState({
    prompt: '',
    response: ''
  });

  useEffect(() => {
    if (isAuthenticated) {
      fetchFeedback();
    }
  }, [isAuthenticated]);

  const fetchFeedback = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:5000/feedback', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setFeedbackList(data.feedback || []);
      } else {
        setMessage('Failed to fetch feedback');
      }
    } catch (error) {
      setMessage('Error fetching feedback: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!isAuthenticated) {
      setMessage('Please login to submit feedback');
      return;
    }

    try {
      setLoading(true);
      const response = await fetch('http://localhost:5000/feedback', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData) // NO SANITIZATION - direct user input
      });

      if (response.ok) {
        const data = await response.json();
        setMessage('Feedback submitted successfully!');
        setFormData({
          prompt: '',
          response: ''
        });
        fetchFeedback(); // Refresh the list
      } else {
        const errorData = await response.json();
        setMessage('Failed to submit feedback: ' + (errorData.error || 'Unknown error'));
      }
    } catch (error) {
      setMessage('Error submitting feedback: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (feedbackId) => {
    if (!confirm('Are you sure you want to delete this feedback?')) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:5000/feedback/${feedbackId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        setMessage('Feedback deleted successfully!');
        fetchFeedback();
      } else {
        setMessage('Failed to delete feedback');
      }
    } catch (error) {
      setMessage('Error deleting feedback: ' + error.message);
    }
  };

  const handleToggleActive = async (feedbackId, currentActive) => {
    try {
      const response = await fetch(`http://localhost:5000/feedback/${feedbackId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ is_active: !currentActive }) // NO SANITIZATION
      });

      if (response.ok) {
        setMessage('Feedback updated successfully!');
        fetchFeedback();
      } else {
        setMessage('Failed to update feedback');
      }
    } catch (error) {
      setMessage('Error updating feedback: ' + error.message);
    }
  };

  return (
    <div className="feedback-container">
      <h1>AI Training Feedback</h1>
      <p className="feedback-description">
        Submit feedback to influence the AI's behavior. This feedback will be used to train and modify the AI's responses.
        <strong>Warning: This system has no input sanitization and can be used for training data poisoning.</strong>
      </p>

      {!isAuthenticated && (
        <div className="auth-warning">
          <p>Please login to submit and manage feedback.</p>
        </div>
      )}

      {isAuthenticated && (
        <div className="feedback-form-section">
          <h2>Submit New Feedback</h2>
          <form onSubmit={handleSubmit} className="feedback-form">
            <div className="form-group">
              <label htmlFor="prompt">Prompt/Question:</label>
              <textarea
                id="prompt"
                value={formData.prompt}
                onChange={(e) => setFormData({...formData, prompt: e.target.value})}
                placeholder="Enter the prompt or question you want to influence..."
                required
                rows={3}
              />
            </div>

            <div className="form-group">
              <label htmlFor="response">Desired Response:</label>
              <textarea
                id="response"
                value={formData.response}
                onChange={(e) => setFormData({...formData, response: e.target.value})}
                placeholder="Enter the response you want the AI to give..."
                required
                rows={3}
              />
            </div>



            <button type="submit" disabled={loading} className="submit-button">
              {loading ? 'Submitting...' : 'Submit Feedback'}
            </button>
          </form>
        </div>
      )}

      {message && (
        <div className={`message ${message.includes('successfully') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}

      <div className="feedback-list-section">
        <h2>Your Feedback</h2>
        {loading ? (
          <p>Loading feedback...</p>
        ) : feedbackList.length === 0 ? (
          <p>No feedback submitted yet.</p>
        ) : (
          <div className="feedback-list">
            {feedbackList.map((feedback) => (
              <div key={feedback.id} className="feedback-item">
                <div className="feedback-header">
                  <span className={`status ${feedback.is_active ? 'active' : 'inactive'}`}>
                    {feedback.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                
                <div className="feedback-content">
                  <div className="feedback-prompt">
                    <strong>Prompt:</strong> {feedback.prompt}
                  </div>
                  <div className="feedback-response">
                    <strong>Response:</strong> {feedback.response}
                  </div>
                </div>
                
                <div className="feedback-footer">
                  <span className="feedback-date">
                    {new Date(feedback.created_at).toLocaleDateString()}
                  </span>
                  <div className="feedback-actions">
                    <button
                      onClick={() => handleToggleActive(feedback.id, feedback.is_active)}
                      className={`toggle-button ${feedback.is_active ? 'deactivate' : 'activate'}`}
                    >
                      {feedback.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                    <button
                      onClick={() => handleDelete(feedback.id)}
                      className="delete-button"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Feedback; 