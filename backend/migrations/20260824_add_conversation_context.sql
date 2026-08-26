ALTER TABLE project_sessions
    ADD COLUMN IF NOT EXISTS conversation_summary JSONB NULL,
    ADD COLUMN IF NOT EXISTS summarized_through_event_id UUID NULL,
    ADD COLUMN IF NOT EXISTS summary_updated_at TIMESTAMPTZ NULL;
