-- ==========================================================================
-- AI20K Data Wherehouse - Database Schema (Dumped directly from LIVE local DB)
-- ==========================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

BEGIN;

-- ------------------------------------------------------------
-- Table: users
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "users" (
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    password_hash TEXT,
    full_name VARCHAR(150),
    is_active BOOLEAN DEFAULT false NOT NULL,
    PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON public.users USING btree (username);
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON public.users USING btree (email);
CREATE UNIQUE INDEX IF NOT EXISTS uq_users_username_casefold ON public.users USING btree (lower((username)::text));
CREATE UNIQUE INDEX IF NOT EXISTS uq_users_email_casefold ON public.users USING btree (lower((email)::text));

-- ------------------------------------------------------------
-- Table: projects
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "projects" (
    name VARCHAR(255) NOT NULL,
    description TEXT,
    domain VARCHAR(100),
    requirement TEXT,
    status VARCHAR(30) NOT NULL,
    user_id UUID NOT NULL,
    id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    requirement_revision INTEGER DEFAULT 0 NOT NULL,
    source_revision INTEGER DEFAULT 0 NOT NULL,
    analyzed_requirement_revision INTEGER DEFAULT 0 NOT NULL,
    analyzed_source_revision INTEGER DEFAULT 0 NOT NULL,
    confirmed_requirement_revision INTEGER DEFAULT 0 NOT NULL,
    derived_analytical_requirement_revision INTEGER DEFAULT 0 NOT NULL,
    PRIMARY KEY ("id"),
    CONSTRAINT projects_user_id_fkey FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_projects_user_id ON public.projects USING btree (user_id);
CREATE INDEX IF NOT EXISTS ix_projects_status ON public.projects USING btree (status);
CREATE INDEX IF NOT EXISTS idx_projects_user_status ON public.projects USING btree (user_id, status);

-- ------------------------------------------------------------
-- Table: revoked_auth_tokens
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "revoked_auth_tokens" (
    jti VARCHAR(64) NOT NULL,
    user_id UUID NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    PRIMARY KEY ("id"),
    CONSTRAINT revoked_auth_tokens_user_id_fkey FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_revoked_auth_tokens_user_id ON public.revoked_auth_tokens USING btree (user_id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_revoked_auth_tokens_jti ON public.revoked_auth_tokens USING btree (jti);
CREATE INDEX IF NOT EXISTS idx_revoked_auth_tokens_expires_at ON public.revoked_auth_tokens USING btree (expires_at);
CREATE INDEX IF NOT EXISTS idx_revoked_auth_tokens_user_id ON public.revoked_auth_tokens USING btree (user_id);

-- ------------------------------------------------------------
-- Table: project_members
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "project_members" (
    project_id UUID NOT NULL,
    user_id UUID NOT NULL,
    role VARCHAR(30) NOT NULL,
    joined_at TIMESTAMP WITH TIME ZONE NOT NULL,
    id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY ("id"),
    CONSTRAINT project_members_project_id_fkey FOREIGN KEY ("project_id") REFERENCES "projects" ("id") ON DELETE CASCADE,
    CONSTRAINT project_members_user_id_fkey FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE,
    CONSTRAINT uq_project_members_project_user UNIQUE ("project_id"),
    CONSTRAINT uq_project_members_project_user UNIQUE ("user_id")
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_project_members_project_user ON public.project_members USING btree (project_id, user_id);
CREATE INDEX IF NOT EXISTS ix_project_members_project_id ON public.project_members USING btree (project_id);
CREATE INDEX IF NOT EXISTS idx_project_members_project_user ON public.project_members USING btree (project_id, user_id);
CREATE INDEX IF NOT EXISTS ix_project_members_user_id ON public.project_members USING btree (user_id);

-- ------------------------------------------------------------
-- Table: requirements
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "requirements" (
    project_id UUID NOT NULL,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(30) NOT NULL,
    id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY ("id"),
    CONSTRAINT requirements_project_id_fkey FOREIGN KEY ("project_id") REFERENCES "projects" ("id") ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_requirements_project_id ON public.requirements USING btree (project_id);

-- ------------------------------------------------------------
-- Table: analytical_requirements
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "analytical_requirements" (
    requirement_id UUID NOT NULL,
    metric VARCHAR(255),
    dimension VARCHAR(255),
    time_granularity VARCHAR(50),
    aggregation_method VARCHAR(50),
    grain TEXT,
    id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY ("id"),
    CONSTRAINT analytical_requirements_requirement_id_fkey FOREIGN KEY ("requirement_id") REFERENCES "requirements" ("id") ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_analytical_requirements_requirement_id ON public.analytical_requirements USING btree (requirement_id);

-- ------------------------------------------------------------
-- Table: requirement_files
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "requirement_files" (
    project_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    file_type VARCHAR(16) NOT NULL,
    location TEXT NOT NULL,
    extracted_text TEXT NOT NULL,
    id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    PRIMARY KEY ("id"),
    CONSTRAINT requirement_files_project_id_fkey FOREIGN KEY ("project_id") REFERENCES "projects" ("id") ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_requirement_files_project_name_ci ON public.requirement_files USING btree (project_id, lower((name)::text));
CREATE INDEX IF NOT EXISTS idx_requirement_files_project ON public.requirement_files USING btree (project_id);

-- ------------------------------------------------------------
-- Table: data_sources
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "data_sources" (
    project_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    location TEXT NOT NULL,
    schema_metadata JSONB,
    id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY ("id"),
    CONSTRAINT data_sources_project_id_fkey FOREIGN KEY ("project_id") REFERENCES "projects" ("id") ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_data_sources_project_type ON public.data_sources USING btree (project_id, type);
CREATE INDEX IF NOT EXISTS ix_data_sources_project_id ON public.data_sources USING btree (project_id);
CREATE INDEX IF NOT EXISTS ix_data_sources_type ON public.data_sources USING btree (type);

-- ------------------------------------------------------------
-- Table: data_models
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "data_models" (
    project_id UUID NOT NULL,
    dbml TEXT NOT NULL,
    revision INTEGER NOT NULL,
    id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    generated_from_requirement_revision INTEGER DEFAULT 1 NOT NULL,
    generated_from_source_revision INTEGER DEFAULT 1 NOT NULL,
    PRIMARY KEY ("id"),
    CONSTRAINT data_models_project_id_fkey FOREIGN KEY ("project_id") REFERENCES "projects" ("id") ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_data_models_project_id ON public.data_models USING btree (project_id);

-- ------------------------------------------------------------
-- Table: data_model_changes
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "data_model_changes" (
    data_model_id UUID NOT NULL,
    base_revision INTEGER NOT NULL,
    proposed_dbml TEXT NOT NULL,
    status VARCHAR(30) NOT NULL,
    user_id UUID NOT NULL,
    id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    base_dbml TEXT NOT NULL,
    PRIMARY KEY ("id"),
    CONSTRAINT data_model_changes_data_model_id_fkey FOREIGN KEY ("data_model_id") REFERENCES "data_models" ("id") ON DELETE CASCADE,
    CONSTRAINT data_model_changes_user_id_fkey FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_data_model_changes_user_id ON public.data_model_changes USING btree (user_id);
CREATE INDEX IF NOT EXISTS ix_data_model_changes_data_model_id ON public.data_model_changes USING btree (data_model_id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_data_model_changes_proposed_model_user ON public.data_model_changes USING btree (data_model_id, user_id) WHERE ((status)::text = 'PROPOSED'::text);

-- ------------------------------------------------------------
-- Table: project_sessions
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "project_sessions" (
    project_id UUID NOT NULL,
    user_id UUID NOT NULL,
    title VARCHAR(255),
    status VARCHAR(30) NOT NULL,
    id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    active_turn_id UUID,
    active_turn_started_at TIMESTAMP WITH TIME ZONE,
    pending_question_id UUID,
    conversation_summary JSONB,
    summarized_through_event_id UUID,
    summary_updated_at TIMESTAMP WITH TIME ZONE,
    purpose VARCHAR(32) DEFAULT 'DATA_MODELING'::character varying NOT NULL,
    base_requirement_revision INTEGER,
    PRIMARY KEY ("id"),
    CONSTRAINT project_sessions_project_id_fkey FOREIGN KEY ("project_id") REFERENCES "projects" ("id") ON DELETE CASCADE,
    CONSTRAINT project_sessions_user_id_fkey FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_project_sessions_project_id ON public.project_sessions USING btree (project_id);
CREATE INDEX IF NOT EXISTS ix_project_sessions_status ON public.project_sessions USING btree (status);
CREATE INDEX IF NOT EXISTS ix_project_sessions_user_id ON public.project_sessions USING btree (user_id);
CREATE INDEX IF NOT EXISTS idx_project_sessions_project_status ON public.project_sessions USING btree (project_id, status);
CREATE INDEX IF NOT EXISTS idx_project_sessions_pending_question ON public.project_sessions USING btree (pending_question_id) WHERE (pending_question_id IS NOT NULL);
CREATE INDEX IF NOT EXISTS idx_project_sessions_project_purpose_status ON public.project_sessions USING btree (project_id, purpose, status);
CREATE UNIQUE INDEX IF NOT EXISTS uq_project_active_requirement_session ON public.project_sessions USING btree (project_id) WHERE (((purpose)::text = 'REQUIREMENT_CLARIFICATION'::text) AND ((status)::text = 'ACTIVE'::text));

-- ------------------------------------------------------------
-- Table: session_events
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "session_events" (
    session_id UUID NOT NULL,
    role VARCHAR(30) NOT NULL,
    type VARCHAR(50) NOT NULL,
    content TEXT,
    metadata JSONB,
    id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    turn_id UUID,
    PRIMARY KEY ("id"),
    CONSTRAINT session_events_session_id_fkey FOREIGN KEY ("session_id") REFERENCES "project_sessions" ("id") ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_session_events_session_created ON public.session_events USING btree (session_id, created_at);
CREATE INDEX IF NOT EXISTS ix_session_events_session_id ON public.session_events USING btree (session_id);
CREATE INDEX IF NOT EXISTS idx_session_events_turn_id ON public.session_events USING btree (turn_id);
CREATE INDEX IF NOT EXISTS idx_session_events_session_turn ON public.session_events USING btree (session_id, turn_id);

-- ------------------------------------------------------------
-- Table: sandbox_configs
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "sandbox_configs" (
    project_id UUID NOT NULL,
    db_type VARCHAR(255) NOT NULL,
    host VARCHAR(255) NOT NULL,
    port INTEGER NOT NULL,
    database_name VARCHAR(255) NOT NULL,
    username VARCHAR(255),
    password TEXT,
    schema_name VARCHAR(255),
    id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    PRIMARY KEY ("id"),
    CONSTRAINT sandbox_configs_project_id_fkey FOREIGN KEY ("project_id") REFERENCES "projects" ("id") ON DELETE CASCADE,
    CONSTRAINT sandbox_configs_project_id_key UNIQUE ("project_id")
);

CREATE UNIQUE INDEX IF NOT EXISTS sandbox_configs_project_id_key ON public.sandbox_configs USING btree (project_id);

COMMIT;