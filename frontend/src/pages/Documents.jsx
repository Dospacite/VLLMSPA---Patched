import React, { useState } from 'react';
import DocumentUpload from '../components/DocumentUpload';
import DocumentSearch from '../components/DocumentSearch';
import './Documents.css';

const Documents = () => {
    const [activeTab, setActiveTab] = useState('upload');

    return (
        <div className="documents-page">
            <div className="page-header">
                <h2>Document Management System</h2>
                <p className="vulnerability-warning">
                    ⚠️ VULNERABLE: This system implements Vector and Embedding Weakness (LLM08) 
                    with no security controls, allowing embedding poisoning and data leakage.
                </p>
            </div>

            <div className="tab-navigation">
                <button
                    className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
                    onClick={() => setActiveTab('upload')}
                >
                    Upload Documents
                </button>
                <button
                    className={`tab-button ${activeTab === 'search' ? 'active' : ''}`}
                    onClick={() => setActiveTab('search')}
                >
                    Search Documents
                </button>
            </div>

            <div className="tab-content">
                {activeTab === 'upload' && (
                    <div className="upload-tab">
                        <DocumentUpload />
                    </div>
                )}
                
                {activeTab === 'search' && (
                    <div className="search-tab">
                        <DocumentSearch />
                    </div>
                )}
            </div>

            <div className="vulnerability-details">
                <h4>Vulnerability Details:</h4>
                <ul>
                    <li><strong>Embedding Poisoning:</strong> No content validation before embedding generation</li>
                    <li><strong>Data Leakage:</strong> No access control on document retrieval</li>
                    <li><strong>No Input Sanitization:</strong> Raw user input directly embedded</li>
                    <li><strong>No Rate Limiting:</strong> Unlimited embedding generation</li>
                    <li><strong>No Authentication:</strong> Anonymous uploads and searches allowed</li>
                    <li><strong>Model Poisoning:</strong> Uses local Ollama model vulnerable to feedback poisoning</li>
                    <li><strong>Unauthorized Deletion:</strong> No authorization checks for document deletion</li>
                </ul>
            </div>
        </div>
    );
};

export default Documents;
