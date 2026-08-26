ALTER TABLE projects
    ADD COLUMN IF NOT EXISTS confirmed_requirement_revision INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS derived_analytical_requirement_revision INTEGER NOT NULL DEFAULT 0;

UPDATE projects
SET confirmed_requirement_revision = analyzed_requirement_revision,
    derived_analytical_requirement_revision = analyzed_requirement_revision
WHERE analyzed_requirement_revision > 0
  AND confirmed_requirement_revision = 0
  AND derived_analytical_requirement_revision = 0;

ALTER TABLE project_sessions
    ADD COLUMN IF NOT EXISTS purpose VARCHAR(32) NOT NULL DEFAULT 'DATA_MODELING',
    ADD COLUMN IF NOT EXISTS base_requirement_revision INTEGER NULL;

UPDATE project_sessions
SET purpose = 'DATA_MODELING'
WHERE purpose IS NULL;

CREATE INDEX IF NOT EXISTS idx_project_sessions_project_purpose_status
    ON project_sessions (project_id, purpose, status);

CREATE UNIQUE INDEX IF NOT EXISTS uq_project_active_requirement_session
    ON project_sessions (project_id)
    WHERE purpose = 'REQUIREMENT_CLARIFICATION' AND status = 'ACTIVE';

CREATE TABLE IF NOT EXISTS requirement_files (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    file_type VARCHAR(16) NOT NULL,
    location TEXT NOT NULL,
    extracted_text TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_requirement_files_project
    ON requirement_files (project_id);

CREATE UNIQUE INDEX IF NOT EXISTS uq_requirement_files_project_name_ci
    ON requirement_files (project_id, LOWER(name));
