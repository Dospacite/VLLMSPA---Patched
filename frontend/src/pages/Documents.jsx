import React, { useState } from 'react';
import DocumentUpload from '../components/DocumentUpload';
import DocumentSearch from '../components/DocumentSearch';
import './Documents.css';

const Documents = () => {
    const [activeTab, setActiveTab] = useState('upload');

    return (
        <div className="documents-page">
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
        </div>
    );
};

export default Documents;
