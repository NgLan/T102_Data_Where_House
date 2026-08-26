ALTER TABLE project_sessions
    ADD COLUMN IF NOT EXISTS pending_question_id UUID NULL;

CREATE INDEX IF NOT EXISTS idx_project_sessions_pending_question
    ON project_sessions (pending_question_id)
    WHERE pending_question_id IS NOT NULL;
