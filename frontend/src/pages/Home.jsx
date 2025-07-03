import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import './Home.css';

export default function Home() {
  const { user, isAuthenticated } = useAuth();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [posting, setPosting] = useState(false);
  const [newMessage, setNewMessage] = useState('');
  const [isPrivate, setIsPrivate] = useState(false);
  const [error, setError] = useState('');
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 20,
    total: 0,
    pages: 0,
    has_next: false,
    has_prev: false
  });

  const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000';

  // Fetch messages
  const fetchMessages = async (page = 1) => {
    try {
      setLoading(true);
      const response = await axios.get(`${BACKEND_URL}/messages?page=${page}&per_page=20`);
      setMessages(response.data.messages);
      setPagination(response.data.pagination);
    } catch (err) {
      setError('Failed to load messages');
      console.error('Error fetching messages:', err);
    } finally {
      setLoading(false);
    }
  };

  // Post a new message
  const handlePostMessage = async (e) => {
    e.preventDefault();
    if (!isAuthenticated || !newMessage.trim()) return;

    try {
      setPosting(true);
      setError('');
      
      const response = await axios.post(`${BACKEND_URL}/messages`, {
        content: newMessage.trim(),
        is_private: isPrivate
      });

      // Add the new message to the beginning of the list
      setMessages(prev => [response.data, ...prev]);
      
      // Reset form
      setNewMessage('');
      setIsPrivate(false);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to post message');
      console.error('Error posting message:', err);
    } finally {
      setPosting(false);
    }
  };

  // Delete a message
  const handleDeleteMessage = async (messageId) => {
    if (!isAuthenticated) return;

    try {
      await axios.delete(`${BACKEND_URL}/messages/${messageId}`);
      setMessages(prev => prev.filter(msg => msg.id !== messageId));
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to delete message');
      console.error('Error deleting message:', err);
    }
  };

  // Load messages on component mount
  useEffect(() => {
    fetchMessages();
  }, []);

  // Format date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="home-container">
      <h1>Message Dashboard</h1>
      
      {/* Post Message Box */}
      <div className="post-message-box">
        <h2>Post a Message</h2>
        <form onSubmit={handlePostMessage}>
          <div className="message-input-group">
            <textarea
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="What's on your mind?"
              disabled={!isAuthenticated}
              className="message-input"
              rows="3"
            />
          </div>
          
          <div className="message-options">
            <label className="private-checkbox">
              <input
                type="checkbox"
                checked={isPrivate}
                onChange={(e) => setIsPrivate(e.target.checked)}
                disabled={!isAuthenticated}
              />
              <span>Private Message</span>
            </label>
            
            <button
              type="submit"
              disabled={!isAuthenticated || !newMessage.trim() || posting}
              className="post-button"
            >
              {posting ? 'Posting...' : isAuthenticated ? 'Post Message' : 'Login to Post'}
            </button>
          </div>
        </form>
        
        {error && <div className="error-message">{error}</div>}
      </div>

      {/* Messages Display */}
      <div className="messages-section">
        <h2>Messages</h2>
        
        {loading ? (
          <div className="loading">Loading messages...</div>
        ) : messages.length === 0 ? (
          <div className="no-messages">No messages yet. Be the first to post!</div>
        ) : (
          <>
            <div className="messages-list">
              {messages.map((message) => (
                <div key={message.id} className="message-card">
                  <div className="message-header">
                    <span className="author">{message.author}</span>
                    <span className="timestamp">{formatDate(message.created_at)}</span>
                    {message.is_private && (
                      <span className="private-badge">Private</span>
                    )}
                  </div>
                  
                  <div className="message-content">
                    {message.content}
                  </div>
                  
                  {isAuthenticated && user?.username === message.author && (
                    <div className="message-actions">
                      <button
                        onClick={() => handleDeleteMessage(message.id)}
                        className="delete-button"
                      >
                        Delete
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
            
            {/* Pagination */}
            {pagination.pages > 1 && (
              <div className="pagination">
                <button
                  onClick={() => fetchMessages(pagination.page - 1)}
                  disabled={!pagination.has_prev}
                  className="pagination-button"
                >
                  Previous
                </button>
                
                <span className="page-info">
                  Page {pagination.page} of {pagination.pages}
                </span>
                
                <button
                  onClick={() => fetchMessages(pagination.page + 1)}
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
    </div>
  );
}