ALTER TABLE project_sessions
ADD COLUMN IF NOT EXISTS requirement_continuation_state VARCHAR(50);

UPDATE project_sessions
SET requirement_continuation_state = 'NOT_REQUIRED'
WHERE requirement_continuation_state IS NULL;

ALTER TABLE project_sessions
ALTER COLUMN requirement_continuation_state SET DEFAULT 'NOT_REQUIRED';

ALTER TABLE project_sessions
ALTER COLUMN requirement_continuation_state SET NOT NULL;
