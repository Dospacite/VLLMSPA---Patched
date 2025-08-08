import React, { useState, useEffect } from 'react';
import './PrivacyStatement.css';

export default function PrivacyStatement() {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchContent();
  }, []);

  const fetchContent = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await fetch('/content/privacy_statement.json');
      if (response.ok) {
        const data = await response.json();
        setContent(data.content);
      } else {
        // Fallback to default content if file doesn't exist
        setContent(`
          <h2>Privacy Statement</h2>
          <p>This is the default privacy statement content. The AI agent can modify this content through the website_content_manager tool.</p>
        `);
      }
    } catch (error) {
      setError('Error loading privacy statement.');
      setContent(`
        <h2>Privacy Statement</h2>
        <p>Error loading content. This demonstrates the excessive agency vulnerability where the AI can modify website content.</p>
      `);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="privacy-container">
        <div className="loading">Loading privacy statement...</div>
      </div>
    );
  }

  return (
    <div className="privacy-container">
      <h1>Privacy Statement</h1>
      {error && <div className="error-message">{error}</div>}
      
      <div className="content" dangerouslySetInnerHTML={{ __html: content }} />
    </div>
  );
}
