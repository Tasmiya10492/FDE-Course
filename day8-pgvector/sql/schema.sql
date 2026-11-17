CREATE TABLE IF NOT EXISTS document_chunks (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    tenant_id TEXT NOT NULL
        CHECK (BTRIM(tenant_id) <> ''),

    content TEXT NOT NULL
        CHECK (BTRIM(content) <> ''),

    embedding VECTOR(768) NOT NULL,

    allowed_roles TEXT[] NOT NULL
        CHECK (
            CARDINALITY(allowed_roles) > 0
            AND ARRAY_POSITION(allowed_roles, NULL) IS NULL
            AND ARRAY_POSITION(allowed_roles, '') IS NULL
        ),

    shared_with_tenants TEXT[] NOT NULL DEFAULT '{}'
        CHECK (
            ARRAY_POSITION(shared_with_tenants, NULL) IS NULL
            AND ARRAY_POSITION(shared_with_tenants, '') IS NULL
            AND tenant_id <> ALL(shared_with_tenants)
        ),

    source TEXT NOT NULL
        CHECK (BTRIM(source) <> ''),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for tenant filtering
CREATE INDEX IF NOT EXISTS idx_document_chunks_tenant
ON document_chunks (tenant_id);

-- Index for role filtering
CREATE INDEX IF NOT EXISTS idx_document_chunks_roles
ON document_chunks USING GIN (allowed_roles);

-- Index for explicit tenant sharing
CREATE INDEX IF NOT EXISTS idx_document_chunks_shared_tenants
ON document_chunks USING GIN (shared_with_tenants);
