-- Day 18: enforce least-privilege access for the application role.

-- Ensure the application can connect to the database and use its schema.
GRANT CONNECT ON DATABASE fde_hr TO hr_app;
GRANT USAGE ON SCHEMA public TO hr_app;

-- Remove previous broad table and sequence permissions.
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM hr_app;
REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM hr_app;

-- Grant only the permissions required by application queries.
GRANT SELECT, INSERT, DELETE
ON TABLE public.document_chunks TO hr_app;

GRANT SELECT, INSERT
ON TABLE public.users TO hr_app;

GRANT SELECT, INSERT, UPDATE, DELETE
ON TABLE public.user_sessions TO hr_app;

GRANT SELECT, INSERT, UPDATE, DELETE
ON TABLE public.login_attempts TO hr_app;

-- Audit events are append-only for the application.
GRANT INSERT
ON TABLE public.audit_events TO hr_app;

GRANT SELECT, INSERT
ON TABLE public.user_records TO hr_app;

-- Identity columns require sequence USAGE for generated IDs.
GRANT USAGE
ON SEQUENCE public.document_chunks_id_seq,
             public.audit_events_id_seq
TO hr_app;

-- Prevent broad default permissions on future objects created by postgres.
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
REVOKE ALL ON TABLES FROM hr_app;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
REVOKE ALL ON SEQUENCES FROM hr_app;
