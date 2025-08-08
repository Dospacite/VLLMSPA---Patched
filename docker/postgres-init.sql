-- Initialize the database with required tables
-- This script runs when the PostgreSQL container starts for the first time

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable vector extension for embeddings (VULNERABLE: No security controls)
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create the users table
CREATE TABLE IF NOT EXISTS "user" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

-- Create the messages table
CREATE TABLE IF NOT EXISTS message (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    is_private BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    author_id UUID NOT NULL REFERENCES "user"(id)
);

-- Create the LLM logs table
CREATE TABLE IF NOT EXISTS llm_log (
    id SERIAL PRIMARY KEY,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    tools_used TEXT,
    intermediate_steps TEXT,
    reasoning_steps TEXT,
    success BOOLEAN NOT NULL DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create document embeddings table (VULNERABLE: No access controls, no content validation)
CREATE TABLE IF NOT EXISTS document_embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(384), -- VULNERABLE: Fixed dimension, no validation
    document_metadata JSONB,
    is_private BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    author_id UUID REFERENCES "user"(id) -- VULNERABLE: Optional, allows anonymous uploads
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_username ON "user"(username);
CREATE INDEX IF NOT EXISTS idx_message_author_id ON message(author_id);
CREATE INDEX IF NOT EXISTS idx_message_created_at ON message(created_at);
CREATE INDEX IF NOT EXISTS idx_llm_log_created_at ON llm_log(created_at);
CREATE INDEX IF NOT EXISTS idx_llm_log_success ON llm_log(success);

-- Create vector similarity search index (VULNERABLE: No access control on search)
CREATE INDEX IF NOT EXISTS idx_document_embeddings_vector 
ON document_embeddings USING ivfflat (embedding vector_cosine_ops);

-- Insert a default admin user (optional - remove if not needed)
-- INSERT INTO "user" (username, password_hash) VALUES 
-- ('admin', 'pbkdf2:sha256:600000$your-hash-here');
