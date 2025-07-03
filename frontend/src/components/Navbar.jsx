// Navbar.jsx
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { isAuthenticated, logout, user } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-logo">Trickster</Link>
      <ul className="navbar-links">
        {/* Always visible navigation links */}
        <li><Link to="/">Home</Link></li>
        <li><Link to="/explore">Explore</Link></li>
        <li><Link to="/ai-chat">AI-Chat</Link></li>
        <li><Link to="/llm-logs">LLM Logs</Link></li>
        <li><Link to="/feedback">Feedback</Link></li>
        
        {/* Authentication-dependent links */}
        {isAuthenticated ? (
          <>
            <li><Link to="/profile">Profile</Link></li>
            <li>
              <button className="auth-button" onClick={handleLogout}>
                Logout
              </button>
            </li>
          </>
        ) : (
          <>
            <li><Link to="/login">Login</Link></li>
            <li><Link to="/register">Register</Link></li>
          </>
        )}
      </ul>
    </nav>
  );
};

export default Navbar;
