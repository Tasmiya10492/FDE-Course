ALTER TABLE document_chunks
    ADD COLUMN IF NOT EXISTS document_id TEXT,
    ADD COLUMN IF NOT EXISTS title TEXT,
    ADD COLUMN IF NOT EXISTS document_type TEXT,
    ADD COLUMN IF NOT EXISTS document_updated_at DATE;

CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id
    ON document_chunks (tenant_id, document_id);
