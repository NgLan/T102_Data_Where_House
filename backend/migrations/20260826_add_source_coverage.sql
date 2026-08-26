ALTER TABLE analytical_requirements
    ADD COLUMN IF NOT EXISTS source_coverage JSONB NOT NULL DEFAULT '[]'::jsonb;

ALTER TABLE projects
    ADD COLUMN IF NOT EXISTS covered_analytical_requirement_revision INTEGER NOT NULL DEFAULT 0;
