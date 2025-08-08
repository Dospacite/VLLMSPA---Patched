import React, { useState } from 'react';
import './DocumentUpload.css';

const DocumentUpload = () => {
    const [content, setContent] = useState('');
    const [metadata, setMetadata] = useState('');
    const [isPrivate, setIsPrivate] = useState(false);
    const [uploadStatus, setUploadStatus] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleUpload = async () => {
        if (!content.trim()) {
            setUploadStatus('Please enter document content');
            return;
        }

        setIsLoading(true);
        setUploadStatus('');

        try {
            const response = await fetch('/api/upload-document', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: content,
                    metadata: metadata ? JSON.parse(metadata) : {},
                    is_private: isPrivate
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                setUploadStatus('Document uploaded successfully!');
                setContent('');
                setMetadata('');
                setIsPrivate(false);
            } else {
                setUploadStatus(`Upload failed: ${result.error}`);
            }
        } catch (error) {
            setUploadStatus(`Upload failed: ${error.message}`);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="document-upload">
            <h3>Upload Document for Embedding</h3>
            <p className="vulnerability-notice">
                ⚠️ VULNERABLE: This feature has no content validation, no rate limiting, 
                and allows anonymous uploads that can poison the embedding model.
            </p>
            
            <div className="upload-form">
                <div className="form-group">
                    <label htmlFor="content">Document Content:</label>
                    <textarea
                        id="content"
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        placeholder="Enter document content to be embedded..."
                        rows={10}
                        className="content-textarea"
                    />
                </div>
                
                <div className="form-group">
                    <label htmlFor="metadata">Metadata (JSON):</label>
                    <textarea
                        id="metadata"
                        value={metadata}
                        onChange={(e) => setMetadata(e.target.value)}
                        placeholder='{"title": "Document Title", "category": "example"}'
                        rows={3}
                        className="metadata-textarea"
                    />
                </div>
                
                <div className="form-group">
                    <label className="checkbox-label">
                        <input
                            type="checkbox"
                            checked={isPrivate}
                            onChange={(e) => setIsPrivate(e.target.checked)}
                        />
                        Mark as Private (VULNERABLE: No access control enforcement)
                    </label>
                </div>
                
                <button 
                    onClick={handleUpload} 
                    disabled={isLoading}
                    className="upload-button"
                >
                    {isLoading ? 'Uploading...' : 'Upload Document'}
                </button>
                
                {uploadStatus && (
                    <div className={`status-message ${uploadStatus.includes('successfully') ? 'success' : 'error'}`}>
                        {uploadStatus}
                    </div>
                )}
            </div>
        </div>
    );
};

export default DocumentUpload;
