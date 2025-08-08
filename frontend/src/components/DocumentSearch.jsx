import React, { useState } from 'react';
import './DocumentSearch.css';

const DocumentSearch = () => {
    const [query, setQuery] = useState('');
    const [includePrivate, setIncludePrivate] = useState(true);
    const [topK, setTopK] = useState(5);
    const [searchResults, setSearchResults] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [searchStatus, setSearchStatus] = useState('');

    const handleSearch = async () => {
        if (!query.trim()) {
            setSearchStatus('Please enter a search query');
            return;
        }

        setIsLoading(true);
        setSearchStatus('');

        try {
            const response = await fetch('/api/search-documents', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    include_private: includePrivate,
                    top_k: topK
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                setSearchResults(result.results);
                setSearchStatus(`Found ${result.total_found} documents`);
            } else {
                setSearchStatus(`Search failed: ${result.error}`);
                setSearchResults([]);
            }
        } catch (error) {
            setSearchStatus(`Search failed: ${error.message}`);
            setSearchResults([]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDeleteDocument = async (docId) => {
        if (!confirm('Are you sure you want to delete this document?')) {
            return;
        }

        try {
            const response = await fetch(`/api/documents/${docId}`, {
                method: 'DELETE',
            });
            
            const result = await response.json();
            
            if (result.success) {
                setSearchResults(prev => prev.filter(doc => doc.id !== docId));
                setSearchStatus('Document deleted successfully');
            } else {
                setSearchStatus(`Delete failed: ${result.error}`);
            }
        } catch (error) {
            setSearchStatus(`Delete failed: ${error.message}`);
        }
    };

    return (
        <div className="document-search">
            <h3>Search Documents Using Vector Embeddings</h3>
            <p className="vulnerability-notice">
                ⚠️ VULNERABLE: This search has no access control and can return private documents. 
                No input sanitization or query validation is performed.
            </p>
            
            <div className="search-form">
                <div className="form-group">
                    <label htmlFor="query">Search Query:</label>
                    <input
                        id="query"
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Enter your search query..."
                        className="query-input"
                    />
                </div>
                
                <div className="search-options">
                    <div className="form-group">
                        <label htmlFor="topK">Number of Results:</label>
                        <select
                            id="topK"
                            value={topK}
                            onChange={(e) => setTopK(parseInt(e.target.value))}
                            className="top-k-select"
                        >
                            <option value={3}>3</option>
                            <option value={5}>5</option>
                            <option value={10}>10</option>
                            <option value={20}>20</option>
                        </select>
                    </div>
                    
                    <div className="form-group">
                        <label className="checkbox-label">
                            <input
                                type="checkbox"
                                checked={includePrivate}
                                onChange={(e) => setIncludePrivate(e.target.checked)}
                            />
                            Include Private Documents (VULNERABLE: No access control)
                        </label>
                    </div>
                </div>
                
                <button 
                    onClick={handleSearch} 
                    disabled={isLoading}
                    className="search-button"
                >
                    {isLoading ? 'Searching...' : 'Search Documents'}
                </button>
                
                {searchStatus && (
                    <div className={`status-message ${searchStatus.includes('successfully') ? 'success' : 'info'}`}>
                        {searchStatus}
                    </div>
                )}
            </div>
            
            {searchResults.length > 0 && (
                <div className="search-results">
                    <h4>Search Results:</h4>
                    <div className="results-list">
                        {searchResults.map((doc, index) => (
                            <div key={doc.id} className={`result-item ${doc.is_private ? 'private' : 'public'}`}>
                                <div className="result-header">
                                    <span className="result-number">#{index + 1}</span>
                                    <span className="similarity-score">
                                        Similarity: {(doc.similarity_score * 100).toFixed(2)}%
                                    </span>
                                    <span className={`privacy-badge ${doc.is_private ? 'private' : 'public'}`}>
                                        {doc.is_private ? 'PRIVATE' : 'PUBLIC'}
                                    </span>
                                </div>
                                
                                <div className="result-content">
                                    <p className="content-text">{doc.content}</p>
                                </div>
                                
                                <div className="result-metadata">
                                    <span className="author">By: {doc.author}</span>
                                    <span className="created-at">{new Date(doc.created_at).toLocaleDateString()}</span>
                                    {doc.metadata && (
                                        <span className="metadata">
                                            Metadata: {JSON.stringify(doc.metadata)}
                                        </span>
                                    )}
                                </div>
                                
                                <div className="result-actions">
                                    <button
                                        onClick={() => handleDeleteDocument(doc.id)}
                                        className="delete-button"
                                        title="Delete document (VULNERABLE: No authorization check)"
                                    >
                                        Delete
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default DocumentSearch;
