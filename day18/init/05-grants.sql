-- Day 18: least-privilege permissions for the application role.

GRANT CONNECT ON DATABASE fde_hr TO hr_app;
GRANT USAGE ON SCHEMA public TO hr_app;

-- Retrieval and document ingestion.
GRANT SELECT, INSERT, DELETE
ON TABLE public.document_chunks TO hr_app;

-- Registration and authentication.
GRANT SELECT, INSERT
ON TABLE public.users TO hr_app;

GRANT SELECT, INSERT, UPDATE, DELETE
ON TABLE public.user_sessions TO hr_app;

GRANT SELECT, INSERT, UPDATE, DELETE
ON TABLE public.login_attempts TO hr_app;

-- Audit events are append-only for the application.
GRANT INSERT
ON TABLE public.audit_events TO hr_app;

-- User-owned records.
GRANT SELECT, INSERT
ON TABLE public.user_records TO hr_app;

-- Identity columns need sequence usage for generated IDs.
GRANT USAGE
ON SEQUENCE public.document_chunks_id_seq,
             public.audit_events_id_seq
TO hr_app;

-- Do not automatically grant broad permissions on future objects.
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
REVOKE ALL ON TABLES FROM hr_app;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
REVOKE ALL ON SEQUENCES FROM hr_app;
