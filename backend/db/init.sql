-- Create research table
CREATE TABLE IF NOT EXISTS research (
    id VARCHAR(255) PRIMARY KEY,
    query TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    sources JSONB DEFAULT '[]'::jsonb,
    results JSONB DEFAULT '[]'::jsonb,
    synthesis TEXT,
    credibility_score FLOAT,
    error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_research_status ON research(status);
CREATE INDEX IF NOT EXISTS idx_research_created_at ON research(created_at DESC);

-- Create function to clean old research
CREATE OR REPLACE FUNCTION clean_old_research() RETURNS void AS $$
BEGIN
    DELETE FROM research 
    WHERE created_at < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;
