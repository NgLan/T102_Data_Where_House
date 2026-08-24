-- ==========================================================================
-- AI20K Data Wherehouse - Clean Database Schema Initialization for Supabase
-- Matches 100% of Backend SQLAlchemy ORM Models
-- ==========================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

BEGIN;

-- 1. Drop existing tables in reverse order if re-initializing cleanly
DROP TABLE IF EXISTS "session_events", "data_model_changes", "analytical_requirements", "sandbox_configs", "requirements", "project_sessions", "project_members", "data_sources", "data_models", "revoked_auth_tokens", "projects", "users" CASCADE;

-- 2. Create tables and indexes
-- ------------------------------------------------------------
-- Table: users
-- ------------------------------------------------------------
CREATE TABLE users (
	username VARCHAR(100) NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	password_hash TEXT, 
	full_name VARCHAR(150), 
	is_active BOOLEAN DEFAULT false NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_users_username ON users (username);
CREATE UNIQUE INDEX ix_users_email ON users (email);

-- ------------------------------------------------------------
-- Table: projects
-- ------------------------------------------------------------
CREATE TABLE projects (
	name VARCHAR(255) NOT NULL, 
	description TEXT, 
	domain VARCHAR(100), 
	requirement TEXT, 
	requirement_revision INTEGER NOT NULL, 
	source_revision INTEGER NOT NULL, 
	analyzed_requirement_revision INTEGER NOT NULL, 
	analyzed_source_revision INTEGER NOT NULL, 
	status VARCHAR(30) NOT NULL, 
	user_id UUID NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX idx_projects_user_status ON projects (user_id, status);
CREATE INDEX ix_projects_user_id ON projects (user_id);
CREATE INDEX ix_projects_status ON projects (status);

-- ------------------------------------------------------------
-- Table: revoked_auth_tokens
-- ------------------------------------------------------------
CREATE TABLE revoked_auth_tokens (
	jti VARCHAR(64) NOT NULL, 
	user_id UUID NOT NULL, 
	expires_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX ix_revoked_auth_tokens_jti ON revoked_auth_tokens (jti);
CREATE INDEX idx_revoked_auth_tokens_expires_at ON revoked_auth_tokens (expires_at);
CREATE INDEX ix_revoked_auth_tokens_user_id ON revoked_auth_tokens (user_id);

-- ------------------------------------------------------------
-- Table: data_models
-- ------------------------------------------------------------
CREATE TABLE data_models (
	project_id UUID NOT NULL, 
	dbml TEXT NOT NULL, 
	revision INTEGER NOT NULL, 
	generated_from_requirement_revision INTEGER NOT NULL, 
	generated_from_source_revision INTEGER NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX ix_data_models_project_id ON data_models (project_id);

-- ------------------------------------------------------------
-- Table: data_sources
-- ------------------------------------------------------------
CREATE TABLE data_sources (
	project_id UUID NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	type VARCHAR(50) NOT NULL, 
	description TEXT, 
	location TEXT NOT NULL, 
	schema_metadata JSONB, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE
);

CREATE INDEX ix_data_sources_project_id ON data_sources (project_id);
CREATE INDEX ix_data_sources_type ON data_sources (type);
CREATE INDEX idx_data_sources_project_type ON data_sources (project_id, type);

-- ------------------------------------------------------------
-- Table: project_members
-- ------------------------------------------------------------
CREATE TABLE project_members (
	project_id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	role VARCHAR(30) NOT NULL, 
	joined_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_project_members_project_user UNIQUE (project_id, user_id), 
	FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE, 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX idx_project_members_project_user ON project_members (project_id, user_id);
CREATE INDEX ix_project_members_user_id ON project_members (user_id);
CREATE INDEX ix_project_members_project_id ON project_members (project_id);

-- ------------------------------------------------------------
-- Table: project_sessions
-- ------------------------------------------------------------
CREATE TABLE project_sessions (
	project_id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	title VARCHAR(255), 
	status VARCHAR(30) NOT NULL, 
	active_turn_id UUID, 
	active_turn_started_at TIMESTAMP WITH TIME ZONE, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE, 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX ix_project_sessions_status ON project_sessions (status);
CREATE INDEX ix_project_sessions_project_id ON project_sessions (project_id);
CREATE INDEX idx_project_sessions_project_status ON project_sessions (project_id, status);
CREATE INDEX ix_project_sessions_user_id ON project_sessions (user_id);

-- ------------------------------------------------------------
-- Table: requirements
-- ------------------------------------------------------------
CREATE TABLE requirements (
	project_id UUID NOT NULL, 
	type VARCHAR(50) NOT NULL, 
	title VARCHAR(255) NOT NULL, 
	description TEXT NOT NULL, 
	priority VARCHAR(30) NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE
);

CREATE INDEX ix_requirements_project_id ON requirements (project_id);

-- ------------------------------------------------------------
-- Table: sandbox_configs
-- ------------------------------------------------------------
CREATE TABLE sandbox_configs (
	project_id UUID NOT NULL, 
	db_type VARCHAR(255) NOT NULL, 
	host VARCHAR(255) NOT NULL, 
	port INTEGER NOT NULL, 
	database_name VARCHAR(100) NOT NULL, 
	username VARCHAR(255), 
	password TEXT, 
	schema_name VARCHAR(100), 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_sandbox_configs_db_type CHECK (db_type = 'POSTGRESQL'), 
	CONSTRAINT ck_sandbox_configs_port CHECK (port BETWEEN 1 AND 65535), 
	CONSTRAINT ck_sandbox_configs_schema_name CHECK (schema_name IS NULL OR schema_name ~ '^[A-Za-z_][A-Za-z0-9_]*$'), 
	UNIQUE (project_id), 
	FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE
);


-- ------------------------------------------------------------
-- Table: analytical_requirements
-- ------------------------------------------------------------
CREATE TABLE analytical_requirements (
	requirement_id UUID NOT NULL, 
	metric VARCHAR(255), 
	dimension VARCHAR(255), 
	time_granularity VARCHAR(50), 
	aggregation_method VARCHAR(50), 
	grain TEXT, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(requirement_id) REFERENCES requirements (id) ON DELETE CASCADE
);

CREATE INDEX ix_analytical_requirements_requirement_id ON analytical_requirements (requirement_id);

-- ------------------------------------------------------------
-- Table: data_model_changes
-- ------------------------------------------------------------
CREATE TABLE data_model_changes (
	data_model_id UUID NOT NULL, 
	base_revision INTEGER NOT NULL, 
	base_dbml TEXT NOT NULL, 
	proposed_dbml TEXT NOT NULL, 
	status VARCHAR(30) NOT NULL, 
	user_id UUID NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(data_model_id) REFERENCES data_models (id) ON DELETE CASCADE, 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX uq_data_model_changes_proposed_model_user ON data_model_changes (data_model_id, user_id) WHERE status = 'PROPOSED';
CREATE INDEX ix_data_model_changes_user_id ON data_model_changes (user_id);
CREATE INDEX ix_data_model_changes_data_model_id ON data_model_changes (data_model_id);

-- ------------------------------------------------------------
-- Table: session_events
-- ------------------------------------------------------------
CREATE TABLE session_events (
	session_id UUID NOT NULL, 
	role VARCHAR(30) NOT NULL, 
	type VARCHAR(50) NOT NULL, 
	content TEXT, 
	turn_id UUID, 
	metadata JSONB, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(session_id) REFERENCES project_sessions (id) ON DELETE CASCADE
);

CREATE INDEX idx_session_events_session_created ON session_events (session_id, created_at);
CREATE INDEX idx_session_events_session_turn ON session_events (session_id, turn_id);
CREATE INDEX ix_session_events_turn_id ON session_events (turn_id);
CREATE INDEX ix_session_events_session_id ON session_events (session_id);

-- ------------------------------------------------------------
-- Default MVP User (Required for MVP actor auth & seed)
-- ------------------------------------------------------------
INSERT INTO public.users (id, username, email, full_name, is_active, created_at, updated_at)
VALUES ('a678ac27-3077-5ef2-8919-5218b2e48791', 'annv', 'an.nguyen@dataworks.vn', 'An Nguyen', true, now(), now())
ON CONFLICT (id) DO NOTHING;

COMMIT;
