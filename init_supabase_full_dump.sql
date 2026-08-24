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


BEGIN;

-- Data for: users (12 rows)
INSERT INTO "users" ("username", "email", "id", "created_at", "updated_at", "password_hash", "full_name", "is_active") VALUES
  ('annv', 'an.nguyen@dataworks.vn', 'a678ac27-3077-5ef2-8919-5218b2e48791'::uuid, '2025-11-02 01:15:00+00:00', '2025-11-02 01:15:00+00:00', NULL, NULL, FALSE),
  ('binhtt', 'binh.tran@dataworks.vn', '729525be-38aa-50fd-8ea9-3fedf76615f1'::uuid, '2025-11-03 02:20:00+00:00', '2025-11-03 02:20:00+00:00', NULL, NULL, FALSE),
  ('longlh', 'long.le@dataworks.vn', '0740e12f-bc1c-556f-9cc7-3ec5332e692e'::uuid, '2025-11-05 03:05:00+00:00', '2025-11-05 03:05:00+00:00', NULL, NULL, FALSE),
  ('huongpt', 'huong.pham@dataworks.vn', '15c1be82-ea36-5205-af17-7fb5947c2027'::uuid, '2025-11-06 07:40:00+00:00', '2025-11-06 07:40:00+00:00', NULL, NULL, FALSE),
  ('ducmh', 'duc.hoang@dataworks.vn', 'c0445430-562e-5472-bea6-06f3a5d6f645'::uuid, '2025-11-10 01:00:00+00:00', '2025-11-10 01:00:00+00:00', NULL, NULL, FALSE),
  ('lanvt', 'lan.vu@dataworks.vn', '4c507932-ae90-57a1-8765-885e45eba112'::uuid, '2025-11-12 04:25:00+00:00', '2025-11-12 04:25:00+00:00', NULL, NULL, FALSE),
  ('baodq', 'bao.dang@dataworks.vn', '85651d6b-4cc0-56ba-ba15-ffc404f10abc'::uuid, '2025-11-15 06:50:00+00:00', '2025-11-15 06:50:00+00:00', NULL, NULL, FALSE),
  ('ngocbt', 'ngoc.bui@dataworks.vn', 'e892c55a-77c6-5c8f-8e00-00da20839ba9'::uuid, '2025-11-20 02:10:00+00:00', '2025-11-20 02:10:00+00:00', NULL, NULL, FALSE),
  ('tungnv', 'tung.ngo@dataworks.vn', '25a6f954-f1cd-567d-88a0-630c4407b254'::uuid, '2025-12-01 01:30:00+00:00', '2025-12-01 01:30:00+00:00', NULL, NULL, FALSE),
  ('maidt', 'mai.do@dataworks.vn', '187ebbb4-aff9-555e-93e8-84718180c565'::uuid, '2025-12-05 08:45:00+00:00', '2025-12-05 08:45:00+00:00', NULL, NULL, FALSE),
  ('mvp_admin', 'admin@ailab.vn', '00000000-0000-0000-0000-000000000001'::uuid, '2026-08-16 09:23:37.923626+00:00', '2026-08-16 09:23:37.923660+00:00', NULL, NULL, FALSE),
  ('NgLan', 'ngoclan271204@gmail.com', '01b19ecb-53ef-4373-99a5-3b0d8bd3af61'::uuid, '2026-08-23 12:12:45.036475+00:00', '2026-08-23 12:12:45.036479+00:00', '$2b$12$TqlRVL0bztEnbOBonFhZPOvRjv/ojB1u7zlPuJtOuKp64yWBaXHIG', 'Nguyễn Ngọc Lan', TRUE)
ON CONFLICT DO NOTHING;

-- Data for: projects (24 rows)
INSERT INTO "projects" ("name", "description", "domain", "requirement", "status", "user_id", "id", "created_at", "updated_at", "requirement_revision", "source_revision", "analyzed_requirement_revision", "analyzed_source_revision", "confirmed_requirement_revision", "derived_analytical_requirement_revision") VALUES
  ('DWH Hồ sơ y tế', NULL, 'custom', 'aaaaaaaaaaaaaaaaaaaaaaaaa', 'ACTIVE', '00000000-0000-0000-0000-000000000001'::uuid, '669dd2e7-e3f3-4c46-a186-cd5c28f3882f'::uuid, '2026-08-16 13:05:25.269260+00:00', '2026-08-16 13:05:25.269277+00:00', 1, 0, 0, 0, 0, 0),
  ('DWH Hồ sơ y tế', NULL, 'custom', 'aaaaaaaaaaaaaaaaaaaaaaaaa', 'ACTIVE', '00000000-0000-0000-0000-000000000001'::uuid, 'ebc843c9-ad12-4e4e-ad45-c38a8057c0fd'::uuid, '2026-08-16 13:05:32.663211+00:00', '2026-08-16 13:05:32.663231+00:00', 1, 0, 0, 0, 0, 0),
  ('DWH Hồ sơ y tế', NULL, 'custom', 'aaaaaaaaaaaaaaaaaaaaaaaaa', 'ACTIVE', '00000000-0000-0000-0000-000000000001'::uuid, '91b0cb2c-33af-4ffe-a16c-272b6effce77'::uuid, '2026-08-16 13:05:33.710000+00:00', '2026-08-16 13:05:33.710006+00:00', 1, 0, 0, 0, 0, 0),
  ('DWH Hồ sơ y tế', NULL, 'custom', 'Aaaaaaaaaaaaaaaaaaaaaaaa', 'ACTIVE', '00000000-0000-0000-0000-000000000001'::uuid, '50816322-8cf7-46ff-b3cf-50dac3837609'::uuid, '2026-08-16 13:06:32.292896+00:00', '2026-08-16 13:06:32.292904+00:00', 1, 0, 0, 0, 0, 0),
  ('Dự án DWH Phân Tích Chuyến Đi & Tài Xế', NULL, 'ride', 'Yêu cầu thiết kế kho dữ liệu tự động cho hệ thống BI', 'ACTIVE', '00000000-0000-0000-0000-000000000001'::uuid, '70949b7e-c7ff-43f0-baa9-3932c3dc0ae3'::uuid, '2026-08-16 09:43:38.552278+00:00', '2026-08-16 09:46:24.862261+00:00', 1, 1, 0, 0, 0, 0),
  ('Kho dữ liệu Vận hành Logistics', 'Data Warehouse theo dõi vận đơn, thời gian giao hàng và hiệu suất tài xế.', 'Logistics', 'Bộ phận vận hành cần theo dõi tỷ lệ giao hàng đúng hạn, thời gian trung chuyển trung bình giữa các kho vùng, hiệu suất từng tài xế/đối tác vận chuyển nhằm tối ưu chi phí logistics hàng tháng.', 'ACTIVE', 'c0445430-562e-5472-bea6-06f3a5d6f645'::uuid, '18525676-8c6b-552b-8de7-a50899ef4b92'::uuid, '2025-11-18 04:00:00+00:00', '2025-11-18 04:00:00+00:00', 1, 1, 0, 0, 0, 0),
  ('ABC', NULL, 'ecommerce', 'Yêu cầu thiết kế kho dữ liệu tự động cho hệ thống BI', 'ACTIVE', '00000000-0000-0000-0000-000000000001'::uuid, '09452af7-3543-42ef-8d8d-439daab81cc7'::uuid, '2026-08-16 09:38:58.644984+00:00', '2026-08-16 09:38:58.644988+00:00', 1, 0, 0, 0, 0, 0),
  ('VIMES - Phân tích lượt khám & chẩn đoán', 'Data mart phân tích lượt khám bệnh, chẩn đoán và đối tượng chi trả viện phí theo khoa/phòng.', 'Y tế', 'Phòng Kế hoạch tổng hợp cần theo dõi số lượt bệnh nhân vào/ra theo từng khoa, phân bố chẩn đoán phổ biến, tỷ lệ bệnh nhân theo đối tượng chi trả (BHYT, Viện phí, Dịch vụ) theo từng quý để phục vụ báo cáo Sở Y tế.', 'ANALYZING', 'a678ac27-3077-5ef2-8919-5218b2e48791'::uuid, '84bdeb46-0eba-564e-8437-833ede4e2718'::uuid, '2025-12-10 03:00:00+00:00', '2025-12-10 03:00:00+00:00', 1, 1, 0, 0, 0, 0),
  ('Kho dữ liệu Ngân hàng bán lẻ', 'Data Warehouse tổng hợp giao dịch, tài khoản khách hàng phục vụ phân tích rủi ro tín dụng.', 'Ngân hàng', 'Khối Quản trị rủi ro cần một kho dữ liệu hợp nhất từ Core Banking và CRM để phân tích hành vi giao dịch bất thường, tính điểm tín dụng khách hàng theo thời gian thực và tuân thủ quy định về bảo mật dữ liệu tài chính cá nhân.', 'ACTIVE', '729525be-38aa-50fd-8ea9-3fedf76615f1'::uuid, 'b2f95613-a6f8-5e35-b6d7-e03bf1cc7aae'::uuid, '2025-11-08 01:30:00+00:00', '2026-08-05 07:10:00+00:00', 1, 1, 0, 0, 0, 0),
  ('Kho dữ liệu Bán lẻ - Chuỗi siêu thị', 'Tổng hợp dữ liệu bán hàng đa kênh (POS, e-commerce) để phân tích doanh thu và tồn kho.', 'Bán lẻ', 'Chuỗi siêu thị mong muốn hợp nhất dữ liệu bán hàng từ hệ thống POS tại 120 cửa hàng và sàn thương mại điện tử để phân tích doanh thu theo ngành hàng/khu vực, dự báo nhu cầu tồn kho và đo lường hiệu quả chương trình khuyến mãi theo tuần.', 'ACTIVE', '0740e12f-bc1c-556f-9cc7-3ec5332e692e'::uuid, '54505703-ca04-5613-9f4a-d2499f12ee3d'::uuid, '2025-11-11 02:15:00+00:00', '2025-11-11 02:15:00+00:00', 1, 1, 0, 0, 0, 0),
  ('Kho dữ liệu Giáo dục - Trường Đại học', 'Tổng hợp dữ liệu tuyển sinh, học vụ và kết quả học tập sinh viên.', 'Giáo dục', 'Phòng Đào tạo cần kho dữ liệu tổng hợp điểm tuyển sinh, tiến độ học tập và tỷ lệ tốt nghiệp theo từng khoa/ngành để hỗ trợ ra quyết định phân bổ chỉ tiêu tuyển sinh hàng năm.', 'ANALYZING', '15c1be82-ea36-5205-af17-7fb5947c2027'::uuid, '8dfcb679-8243-5be9-b8ee-b2bde7997277'::uuid, '2025-12-02 01:45:00+00:00', '2025-12-02 01:45:00+00:00', 1, 1, 0, 0, 0, 0),
  ('Kho dữ liệu Sản xuất - Nhà máy', 'Theo dõi sản lượng, tỷ lệ lỗi và hiệu suất dây chuyền sản xuất (OEE).', 'Sản xuất', 'Nhà máy cần một kho dữ liệu tổng hợp từ hệ thống MES và cảm biến IoT để tính chỉ số OEE theo từng dây chuyền, phân tích nguyên nhân dừng máy và tỷ lệ sản phẩm lỗi theo ca làm việc.', 'ACTIVE', '4c507932-ae90-57a1-8765-885e45eba112'::uuid, 'ef1e1ed3-a3b9-5fd0-86a5-2beec97bdf48'::uuid, '2025-12-08 06:00:00+00:00', '2025-12-08 06:00:00+00:00', 1, 1, 0, 0, 0, 0),
  ('Kho dữ liệu Bảo hiểm nhân thọ', 'Phân tích hồ sơ hợp đồng, yêu cầu bồi thường và rủi ro gian lận.', 'Bảo hiểm', 'Công ty bảo hiểm cần hợp nhất dữ liệu hợp đồng, hồ sơ yêu cầu bồi thường (claim) và lịch sử thanh toán để phát hiện sớm các dấu hiệu gian lận bảo hiểm và tính tỷ lệ bồi thường theo sản phẩm.', 'ARCHIVED', '85651d6b-4cc0-56ba-ba15-ffc404f10abc'::uuid, '53774151-12ea-53d4-9d34-ebccfd4a2594'::uuid, '2025-10-20 01:00:00+00:00', '2025-12-01 03:00:00+00:00', 1, 1, 0, 0, 0, 0),
  ('Kho dữ liệu Viễn thông - Thuê bao', 'Tổng hợp dữ liệu cước, lưu lượng và tỷ lệ rời mạng (churn) của thuê bao.', 'Viễn thông', 'Bộ phận Chăm sóc khách hàng cần theo dõi lưu lượng data/thoại sử dụng, doanh thu ARPU và dự báo tỷ lệ rời mạng theo từng gói cước nhằm xây dựng chương trình giữ chân khách hàng.', 'ACTIVE', 'e892c55a-77c6-5c8f-8e00-00da20839ba9'::uuid, 'f8c4432f-0252-5275-a581-958039b98639'::uuid, '2025-12-15 02:30:00+00:00', '2025-12-15 02:30:00+00:00', 1, 1, 0, 0, 0, 0),
  ('VIMES - Kho dữ liệu Hồ sơ bệnh án lưu trữ', 'Bệnh viện cần một kho dữ liệu tổng hợp thông tin hồ sơ bệnh án đã lưu trữ (Hồ sơ lưu trữ, Thông tin bệnh nhân, Danh sách bệnh nhân) để ban giám đốc theo dõi số lượng hồ sơ nhập/xuất kho theo tháng, tỷ lệ lấp đầy của từng Kho/Tủ/Ngăn, thời gian lưu trữ trung bình theo khoa, đồng thời đảm bảo dữ liệu cá nhân bệnh nhân được ẩn danh trước khi đưa vào các báo cáo phân tích.', 'Y tế', 'Bệnh viện cần một kho dữ liệu tổng hợp thông tin hồ sơ bệnh án đã lưu trữ (Hồ sơ lưu trữ, Thông tin bệnh nhân, Danh sách bệnh nhân) để ban giám đốc theo dõi số lượng hồ sơ nhập/xuất kho theo tháng, tỷ lệ lấp đầy của từng Kho/Tủ/Ngăn, thời gian lưu trữ trung bình theo khoa, đồng thời đảm bảo dữ liệu cá nhân bệnh nhân được ẩn danh trước khi đưa vào các báo cáo phân tích.', 'ACTIVE', 'a678ac27-3077-5ef2-8919-5218b2e48791'::uuid, '7e621a51-f48a-53bf-927d-f415ae6c9249'::uuid, '2025-11-04 02:00:00+00:00', '2026-08-16 14:35:29.196870+00:00', 1, 1, 0, 0, 0, 0),
  ('Hồ sơ bệnh án', 'TÀI LIỆU YÊU CẦU NGHIỆP VỤ QUẢN LÝ & PHÂN TÍCH HỒ SƠ BỆNH ÁN Hệ thống Phân tích & Thiết kế Kho Dữ liệu Bệnh viện (Healthcare Data Warehouse) 1. Toàn Văn Yêu Cầu Nghiệp Vụ (Raw Requirements) Bệnh viện cần xây dựng Kho dữ liệu (Data Warehouse) để quản lý và phân tích hồ sơ bệnh án lưu trữ, phục vụ các mục tiêu chính sau đây: Phân tích tình hình khám chữa bệnh: Theo dõi số lượng bệnh nhân, thời gian điều trị trung bình (tính từ thời gian vào viện đến ngày ra viện) phân theo từng khoa phòng (vào từ khoa nào, ra từ khoa nào), nhóm tuổi và giới tính. Quản lý đối tượng bệnh nhân: Thống kê cơ cấu bệnh nhân theo diện chi trả (BHYT, BHYT Quân, Miễn phí, Dịch vụ) và loại hình điều trị (Nội trú, Ngoại trú). Tối ưu hóa công tác lưu trữ hồ sơ: Quản lý vị trí vật lý lưu trữ hồ sơ bệnh án (theo Kho, Tủ, Ngăn, Kệ, Ký hiệu) và trạng thái hồ sơ (đang lưu trữ, chờ đưa vào kho, cần bổ sung xét nghiệm) để phục vụ tra cứu nhanh chóng và bảo mật thông tin cá nhân của bệnh nhân. 2. Mục Tiêu Phân Tích Dữ Liệu (Analytical Goals) 3. Yêu Cầu Kỹ Thuật & Ràng Buộc Bảo Mật (Technical Constraints) Ẩn danh hóa dữ liệu nhạy cảm (PII Protection): Thông tin cá nhân nhạy cảm của bệnh nhân (Họ và tên, Địa chỉ chi tiết, Số định danh) phải được bộ lọc PII Guard tự động nhận diện và ẩn danh trước khi chuyển qua LLM API. Khóa thay thế (Surrogate Keys): Toàn bộ bảng Fact và Dimension trong Data Warehouse phải sử dụng Surrogate Key dạng số nguyên tự tăng hoặc chuỗi UUID (ví dụ: benhnhan_sk, khoa_sk, vitri_sk) làm Primary Key thay vì dùng trực tiếp số hồ sơ y tế tự nhiên. Chuẩn hóa mô hình chiều Kimball (Star Schema): Thiết kế theo mô hình hình sao (Star Schema) tối ưu hóa truy vấn phân tích đa chiều OLAP, liên kết rõ ràng giữa bảng Fact trung tâm và các bảng Dimension xung quanh. Môi trường kiểm thử cách ly (Sandbox Testing): Toàn bộ câu lệnh DDL SQL được sinh ra phải chạy thử nghiệm thành công trên sandbox_schema.* trước khi bàn giao cho người dùng duyệt. Mã bài toán: | DW-HEALTHCARE-01 Lĩnh vực (Domain): | Y tế / Quản lý Bệnh viện (Healthcare & Hospital Information System) Dữ liệu nguồn đính kèm: | 4 tệp CSV (DanhSachBenhNhan.csv, ThongTinBenhNhan.csv, ThongtinHoSoLuuTru.csv, DanhSachHoSoLuuTru.csv) Chỉ số đo lường (Metrics / Measures) | Chiều phân tích (Dimensions) | Mức độ chi tiết (Grain) | Phương thức tổng hợp (Aggregation) Thời gian điều trị trung bình (ngày) | Khoa vào viện, Khoa ra viện, Nhóm tuổi, Giới tính | Từng lượt điều trị / bệnh án | AVG(DATEDIFF(ngay_ra, ngay_vao)) Số lượng bệnh nhân tiếp nhận | Diện đối tượng chi trả, Loại hình điều trị (Nội/Ngoại trú) | Từng bệnh nhân / Lượt vào viện | COUNT(DISTINCT so_ho_so) Số lượng hồ sơ lưu trữ theo trạng thái | Trạng thái hồ sơ, Vị trí Kho, Tủ, Ngăn, Kệ | Từng hồ sơ bệnh án lưu trữ | COUNT(so_benh_an)', 'ride', 'TÀI LIỆU YÊU CẦU NGHIỆP VỤ QUẢN LÝ & PHÂN TÍCH HỒ SƠ BỆNH ÁN Hệ thống Phân tích & Thiết kế Kho Dữ liệu Bệnh viện (Healthcare Data Warehouse) 1. Toàn Văn Yêu Cầu Nghiệp Vụ (Raw Requirements) Bệnh viện cần xây dựng Kho dữ liệu (Data Warehouse) để quản lý và phân tích hồ sơ bệnh án lưu trữ, phục vụ các mục tiêu chính sau đây: Phân tích tình hình khám chữa bệnh: Theo dõi số lượng bệnh nhân, thời gian điều trị trung bình (tính từ thời gian vào viện đến ngày ra viện) phân theo từng khoa phòng (vào từ khoa nào, ra từ khoa nào), nhóm tuổi và giới tính. Quản lý đối tượng bệnh nhân: Thống kê cơ cấu bệnh nhân theo diện chi trả (BHYT, BHYT Quân, Miễn phí, Dịch vụ) và loại hình điều trị (Nội trú, Ngoại trú). Tối ưu hóa công tác lưu trữ hồ sơ: Quản lý vị trí vật lý lưu trữ hồ sơ bệnh án (theo Kho, Tủ, Ngăn, Kệ, Ký hiệu) và trạng thái hồ sơ (đang lưu trữ, chờ đưa vào kho, cần bổ sung xét nghiệm) để phục vụ tra cứu nhanh chóng và bảo mật thông tin cá nhân của bệnh nhân. 2. Mục Tiêu Phân Tích Dữ Liệu (Analytical Goals) 3. Yêu Cầu Kỹ Thuật & Ràng Buộc Bảo Mật (Technical Constraints) Ẩn danh hóa dữ liệu nhạy cảm (PII Protection): Thông tin cá nhân nhạy cảm của bệnh nhân (Họ và tên, Địa chỉ chi tiết, Số định danh) phải được bộ lọc PII Guard tự động nhận diện và ẩn danh trước khi chuyển qua LLM API. Khóa thay thế (Surrogate Keys): Toàn bộ bảng Fact và Dimension trong Data Warehouse phải sử dụng Surrogate Key dạng số nguyên tự tăng hoặc chuỗi UUID (ví dụ: benhnhan_sk, khoa_sk, vitri_sk) làm Primary Key thay vì dùng trực tiếp số hồ sơ y tế tự nhiên. Chuẩn hóa mô hình chiều Kimball (Star Schema): Thiết kế theo mô hình hình sao (Star Schema) tối ưu hóa truy vấn phân tích đa chiều OLAP, liên kết rõ ràng giữa bảng Fact trung tâm và các bảng Dimension xung quanh. Môi trường kiểm thử cách ly (Sandbox Testing): Toàn bộ câu lệnh DDL SQL được sinh ra phải chạy thử nghiệm thành công trên sandbox_schema.* trước khi bàn giao cho người dùng duyệt. Mã bài toán: | DW-HEALTHCARE-01 Lĩnh vực (Domain): | Y tế / Quản lý Bệnh viện (Healthcare & Hospital Information System) Dữ liệu nguồn đính kèm: | 4 tệp CSV (DanhSachBenhNhan.csv, ThongTinBenhNhan.csv, ThongtinHoSoLuuTru.csv, DanhSachHoSoLuuTru.csv) Chỉ số đo lường (Metrics / Measures) | Chiều phân tích (Dimensions) | Mức độ chi tiết (Grain) | Phương thức tổng hợp (Aggregation) Thời gian điều trị trung bình (ngày) | Khoa vào viện, Khoa ra viện, Nhóm tuổi, Giới tính | Từng lượt điều trị / bệnh án | AVG(DATEDIFF(ngay_ra, ngay_vao)) Số lượng bệnh nhân tiếp nhận | Diện đối tượng chi trả, Loại hình điều trị (Nội/Ngoại trú) | Từng bệnh nhân / Lượt vào viện | COUNT(DISTINCT so_ho_so) Số lượng hồ sơ lưu trữ theo trạng thái | Trạng thái hồ sơ, Vị trí Kho, Tủ, Ngăn, Kệ | Từng hồ sơ bệnh án lưu trữ | COUNT(so_benh_an)', 'ACTIVE', 'a678ac27-3077-5ef2-8919-5218b2e48791'::uuid, '0baed64b-d380-4a01-a64b-265af7059568'::uuid, '2026-08-17 09:03:35.755151+00:00', '2026-08-17 09:24:51.288697+00:00', 1, 1, 0, 0, 0, 0),
  ('Kho dữ liệu Thương mại điện tử', 'Data Warehouse phân tích hành vi mua sắm, giỏ hàng bỏ dở và hiệu quả marketing.', 'Thương mại điện tử', 'Sàn thương mại điện tử cần kho dữ liệu hợp nhất hành vi duyệt web, giỏ hàng, đơn hàng và chi phí quảng cáo để tối ưu tỷ lệ chuyển đổi và phân khúc khách hàng theo giá trị vòng đời (CLV).', 'ACTIVE', '25a6f954-f1cd-567d-88a0-630c4407b254'::uuid, '6268eced-f86b-5e52-b0a9-262a806879e9'::uuid, '2026-01-05 03:00:00+00:00', '2026-01-05 03:00:00+00:00', 1, 1, 0, 0, 0, 0),
  ('Dự án DWH Phân Tích Chuyến Đi & Tài Xế', NULL, 'ecommerce', 'Hệ thống Data Warehouse phục vụ báo cáo và phân tích hoạt động kinh doanh dịch vụ gọi xe:
- Theo dõi doanh thu chuyến đi theo ngày/tháng/quý và theo từng khu vực hoạt động.
- Đo lường hiệu suất tài xế (tỷ lệ hoàn thành chuyến, đánh giá rating, thu nhập bình quân).
- Phân tích hành vi khách hàng (tần suất đặt chuyến, tỷ lệ sử dụng voucher giảm giá).
- Báo cáo tỷ lệ hủy chuyến theo khung giờ cao điểm để tối ưu thuật toán điều phối tài xế.', 'ACTIVE', '00000000-0000-0000-0000-000000000001'::uuid, '144b02e3-6867-41af-b563-096a06fd83e2'::uuid, '2026-08-16 09:27:57.386717+00:00', '2026-08-16 09:28:08.651727+00:00', 1, 1, 0, 0, 0, 0),
  ('Dự án DWH Phân Tích Chuyến Đi & Tài Xế', NULL, 'ride', 'Hệ thống Data Warehouse phục vụ báo cáo và phân tích hoạt động kinh doanh dịch vụ gọi xe:
- Theo dõi doanh thu chuyến đi theo ngày/tháng/quý và theo từng khu vực hoạt động.
- Đo lường hiệu suất tài xế (tỷ lệ hoàn thành chuyến, đánh giá rating, thu nhập bình quân).
- Phân tích hành vi khách hàng (tần suất đặt chuyến, tỷ lệ sử dụng voucher giảm giá).
- Báo cáo tỷ lệ hủy chuyến theo khung giờ cao điểm để tối ưu thuật toán điều phối tài xế.', 'ACTIVE', '00000000-0000-0000-0000-000000000001'::uuid, 'ae94fe31-2a34-4652-a9ed-03d154eba768'::uuid, '2026-08-16 09:39:21.998395+00:00', '2026-08-16 09:39:21.998398+00:00', 1, 1, 0, 0, 0, 0),
  ('Dự án DWH Phân Tích Chuyến Đi & Tài Xế', NULL, 'ride', 'Hệ thống Data Warehouse phục vụ báo cáo và phân tích hoạt động kinh doanh dịch vụ gọi xe:
- Theo dõi doanh thu chuyến đi theo ngày/tháng/quý và theo từng khu vực hoạt động.
- Đo lường hiệu suất tài xế (tỷ lệ hoàn thành chuyến, đánh giá rating, thu nhập bình quân).
- Phân tích hành vi khách hàng (tần suất đặt chuyến, tỷ lệ sử dụng voucher giảm giá).
- Báo cáo tỷ lệ hủy chuyến theo khung giờ cao điểm để tối ưu thuật toán điều phối tài xế.', 'ACTIVE', '00000000-0000-0000-0000-000000000001'::uuid, '29e97dc3-2e93-4430-9a12-9b3992541f31'::uuid, '2026-08-16 09:40:18.599699+00:00', '2026-08-16 09:40:18.599702+00:00', 1, 1, 0, 0, 0, 0),
  ('ABC', NULL, 'ride', NULL, 'ACTIVE', 'a678ac27-3077-5ef2-8919-5218b2e48791'::uuid, 'b05c0f83-d93a-439b-bb1a-f7c109af8201'::uuid, '2026-08-22 02:07:39.128880+00:00', '2026-08-22 06:23:45.610544+00:00', 0, 4, 0, 4, 0, 0),
  ('DWH VinMec', NULL, 'healthcare', '# Tài Liệu Yêu Cầu Nghiệp Vụ — Quản Lý & Phân Tích Hồ Sơ Bệnh Án (Y Tế) > **Mã bài toán:** DW-HEALTHCARE-01 > **Lĩnh vực (Domain):** Y tế / Quản lý Bệnh viện (Healthcare & Hospital Information System) > **Dữ liệu nguồn kèm theo:** 4 tệp CSV trong thư mục `eval/sample/` (`DanhSachBenhNhan.csv`, `ThongTinBenhNhan.csv`, `ThongtinHoSoLuuTru.csv`, `DanhSachHoSoLuuTru.csv`) --- ## 📋 Toàn Văn Yêu Cầu Nghiệp Vụ (Raw Requirement) Bệnh viện cần xây dựng Kho dữ liệu (Data Warehouse) để quản lý và phân tích hồ sơ bệnh án lưu trữ, phục vụ các mục tiêu sau: 1. **Phân tích tình hình khám chữa bệnh**: Theo dõi số lượng bệnh nhân, thời gian điều trị trung bình (tính từ thời gian vào viện đến ngày ra viện) phân theo từng khoa phòng (vào từ khoa nào, ra từ khoa nào), nhóm tuổi và giới tính. 2. **Quản lý đối tượng bệnh nhân**: Thống kê cơ cấu bệnh nhân theo diện chi trả (BHYT, BHYT Quân, Miễn phí, Dịch vụ) và loại hình điều trị (Nội trú, Ngoại trú). 3. **Tối ưu hóa công tác lưu trữ hồ sơ**: Quản lý vị trí vật lý lưu trữ hồ sơ bệnh án (theo Kho, Tủ, Ngăn, Kệ, Ký hiệu) và trạng thái hồ sơ (đang lưu trữ, chờ đưa vào kho, cần bổ sung xét nghiệm) để phục vụ tra cứu nhanh chóng và bảo mật thông tin cá nhân của bệnh nhân. --- ## 🎯 Mục Tiêu Phân Tích Dữ Liệu (Analytical Goals) | Chỉ số cần đo lường (Metrics / Measures) | Chiều phân tích (Dimensions) | Mức độ chi tiết (Grain) | Phương thức tổng hợp (Aggregation) | | :--- | :--- | :--- | :--- | | **Thời gian điều trị trung bình (ngày)** | Khoa vào viện, Khoa ra viện, Nhóm tuổi, Giới tính | Từng lượt điều trị / bệnh án | `AVG(DATEDIFF(ngay_ra, ngay_vao))` | | **Số lượng bệnh nhân tiếp nhận** | Diện đối tượng chi trả, Loại hình điều trị (Nội/Ngoại trú) | Từng bệnh nhân / Lượt vào viện | `COUNT(DISTINCT so_ho_so)` | | **Số lượng hồ sơ lưu trữ theo trạng thái** | Trạng thái hồ sơ, Vị trí Kho, Tủ, Ngăn, Kệ | Từng hồ sơ bệnh án lưu trữ | `COUNT(so_benh_an)` | --- ## 🔒 Yêu Cầu Kỹ Thuật & Bảo Mật (Technical & Security Constraints) - **Ẩn danh hóa dữ liệu (PII Protection)**: Thông tin cá nhân nhạy cảm của bệnh nhân (Họ và tên, Địa chỉ chi tiết) phải được PII Guard ẩn danh trước khi chuyển qua LLM API. - **Khóa thay thế (Surrogate Keys)**: Toàn bộ bảng Fact và Dimension trong Data Warehouse phải sử dụng Surrogate Key dạng số nguyên hoặc UUID (ví dụ: `benhnhan_sk`, `khoa_sk`, `vitri_sk`) thay vì dùng trực tiếp số hồ sơ y tế. - **Chuẩn hóa mô hình**: Thiết kế theo mô hình hình sao (Star Schema) tối ưu truy vấn OLAP, liên kết khóa ngoại rõ ràng.', 'ACTIVE', 'a678ac27-3077-5ef2-8919-5218b2e48791'::uuid, '0772523a-7235-410b-8eea-ee711baa62e0'::uuid, '2026-08-22 09:52:25.569308+00:00', '2026-08-22 11:09:44.470691+00:00', 1, 1, 1, 1, 1, 1),
  ('DWH VinMec', NULL, 'healthcare', '# Tài Liệu Yêu Cầu Nghiệp Vụ — Quản Lý & Phân Tích Hồ Sơ Bệnh Án (Y Tế) > **Mã bài toán:** DW-HEALTHCARE-01 > **Lĩnh vực (Domain):** Y tế / Quản lý Bệnh viện (Healthcare & Hospital Information System) > **Dữ liệu nguồn kèm theo:** 4 tệp CSV trong thư mục `eval/sample/` (`DanhSachBenhNhan.csv`, `ThongTinBenhNhan.csv`, `ThongtinHoSoLuuTru.csv`, `DanhSachHoSoLuuTru.csv`) --- ## 📋 Toàn Văn Yêu Cầu Nghiệp Vụ (Raw Requirement) Bệnh viện cần xây dựng Kho dữ liệu (Data Warehouse) để quản lý và phân tích hồ sơ bệnh án lưu trữ, phục vụ các mục tiêu sau: 1. **Phân tích tình hình khám chữa bệnh**: Theo dõi số lượng bệnh nhân, thời gian điều trị trung bình (tính từ thời gian vào viện đến ngày ra viện) phân theo từng khoa phòng (vào từ khoa nào, ra từ khoa nào), nhóm tuổi và giới tính. 2. **Quản lý đối tượng bệnh nhân**: Thống kê cơ cấu bệnh nhân theo diện chi trả (BHYT, BHYT Quân, Miễn phí, Dịch vụ) và loại hình điều trị (Nội trú, Ngoại trú). 3. **Tối ưu hóa công tác lưu trữ hồ sơ**: Quản lý vị trí vật lý lưu trữ hồ sơ bệnh án (theo Kho, Tủ, Ngăn, Kệ, Ký hiệu) và trạng thái hồ sơ (đang lưu trữ, chờ đưa vào kho, cần bổ sung xét nghiệm) để phục vụ tra cứu nhanh chóng và bảo mật thông tin cá nhân của bệnh nhân. --- ## 🎯 Mục Tiêu Phân Tích Dữ Liệu (Analytical Goals) | Chỉ số cần đo lường (Metrics / Measures) | Chiều phân tích (Dimensions) | Mức độ chi tiết (Grain) | Phương thức tổng hợp (Aggregation) | | :--- | :--- | :--- | :--- | | **Thời gian điều trị trung bình (ngày)** | Khoa vào viện, Khoa ra viện, Nhóm tuổi, Giới tính | Từng lượt điều trị / bệnh án | `AVG(DATEDIFF(ngay_ra, ngay_vao))` | | **Số lượng bệnh nhân tiếp nhận** | Diện đối tượng chi trả, Loại hình điều trị (Nội/Ngoại trú) | Từng bệnh nhân / Lượt vào viện | `COUNT(DISTINCT so_ho_so)` | | **Số lượng hồ sơ lưu trữ theo trạng thái** | Trạng thái hồ sơ, Vị trí Kho, Tủ, Ngăn, Kệ | Từng hồ sơ bệnh án lưu trữ | `COUNT(so_benh_an)` | --- ## 🔒 Yêu Cầu Kỹ Thuật & Bảo Mật (Technical & Security Constraints) - **Ẩn danh hóa dữ liệu (PII Protection)**: Thông tin cá nhân nhạy cảm của bệnh nhân (Họ và tên, Địa chỉ chi tiết) phải được PII Guard ẩn danh trước khi chuyển qua LLM API. - **Khóa thay thế (Surrogate Keys)**: Toàn bộ bảng Fact và Dimension trong Data Warehouse phải sử dụng Surrogate Key dạng số nguyên hoặc UUID (ví dụ: `benhnhan_sk`, `khoa_sk`, `vitri_sk`) thay vì dùng trực tiếp số hồ sơ y tế. - **Chuẩn hóa mô hình**: Thiết kế theo mô hình hình sao (Star Schema) tối ưu truy vấn OLAP, liên kết khóa ngoại rõ ràng.', 'ACTIVE', '01b19ecb-53ef-4373-99a5-3b0d8bd3af61'::uuid, '2da8c727-32f8-4ce2-9528-ae87ee60077d'::uuid, '2026-08-23 12:15:53.232618+00:00', '2026-08-23 12:23:26.323220+00:00', 1, 3, 1, 3, 1, 1),
  ('test2', NULL, 'ride', '"Bệnh viện cần thiết kế Data Warehouse quản lý tình hình bán thuốc và cấp phát đơn thuốc. Cần đo lường tổng doanh thu nhà thuốc, số lượng thuốc đã phát và thời gian chờ nhận thuốc của bệnh nhân theo từng loại thuốc và từng đối tượng bệnh nhân."', 'ACTIVE', '01b19ecb-53ef-4373-99a5-3b0d8bd3af61'::uuid, 'c6e50b32-d59d-41d5-b634-618d8a4286c8'::uuid, '2026-08-24 08:57:35.796016+00:00', '2026-08-24 16:08:05.741515+00:00', 1, 1, 1, 0, 1, 0)
ON CONFLICT DO NOTHING;

-- Data for: revoked_auth_tokens (1 rows)
INSERT INTO "revoked_auth_tokens" ("jti", "user_id", "expires_at", "id", "created_at", "updated_at") VALUES
  ('5c635587-6c48-4d0e-a3ef-ee0e455dbbbb', '01b19ecb-53ef-4373-99a5-3b0d8bd3af61'::uuid, '2026-08-24 16:30:03+00:00', '15dd4a16-2691-4af8-a70b-c66a1b1dfcb0'::uuid, '2026-08-24 16:00:14.157610+00:00', '2026-08-24 16:00:14.157616+00:00')
ON CONFLICT DO NOTHING;

-- Data for: project_members (36 rows)
INSERT INTO "project_members" ("project_id", "user_id", "role", "joined_at", "id", "created_at", "updated_at") VALUES
  ('7e621a51-f48a-53bf-927d-f415ae6c9249'::uuid, 'a678ac27-3077-5ef2-8919-5218b2e48791'::uuid, 'OWNER', '2025-11-04 02:05:00+00:00', '154b2a3f-475b-5b7d-968a-ea7a72418443'::uuid, '2025-11-04 02:05:00+00:00', '2025-11-04 02:05:00+00:00'),
  ('7e621a51-f48a-53bf-927d-f415ae6c9249'::uuid, '15c1be82-ea36-5205-af17-7fb5947c2027'::uuid, 'MEMBER', '2025-11-04 02:05:00+00:00', 'fcbc80ec-30f7-5b69-ba9b-64901b5a1a2a'::uuid, '2025-11-04 02:05:00+00:00', '2025-11-04 02:05:00+00:00'),
  ('7e621a51-f48a-53bf-927d-f415ae6c9249'::uuid, 'e892c55a-77c6-5c8f-8e00-00da20839ba9'::uuid, 'MEMBER', '2025-11-04 02:05:00+00:00', '1e5e7b3b-2ae1-59e9-b37a-885435a332a5'::uuid, '2025-11-04 02:05:00+00:00', '2025-11-04 02:05:00+00:00'),
  ('84bdeb46-0eba-564e-8437-833ede4e2718'::uuid, 'a678ac27-3077-5ef2-8919-5218b2e48791'::uuid, 'OWNER', '2025-12-10 03:05:00+00:00', '6456a3f4-67af-5e09-b466-ed4b71356659'::uuid, '2025-12-10 03:05:00+00:00', '2025-12-10 03:05:00+00:00'),
  ('84bdeb46-0eba-564e-8437-833ede4e2718'::uuid, '4c507932-ae90-57a1-8765-885e45eba112'::uuid, 'MEMBER', '2025-12-10 03:05:00+00:00', '1b6f9efb-4e2c-588b-b616-385ed10e7275'::uuid, '2025-12-10 03:05:00+00:00', '2025-12-10 03:05:00+00:00'),
  ('b2f95613-a6f8-5e35-b6d7-e03bf1cc7aae'::uuid, '729525be-38aa-50fd-8ea9-3fedf76615f1'::uuid, 'OWNER', '2025-11-08 01:35:00+00:00', 'e45fc8fe-bd81-54a7-b23c-d703c9d11b17'::uuid, '2025-11-08 01:35:00+00:00', '2025-11-08 01:35:00+00:00'),
  ('b2f95613-a6f8-5e35-b6d7-e03bf1cc7aae'::uuid, '0740e12f-bc1c-556f-9cc7-3ec5332e692e'::uuid, 'MEMBER', '2025-11-08 01:35:00+00:00', '8cbc4908-2cb3-5a02-ac17-dded2427e7b1'::uuid, '2025-11-08 01:35:00+00:00', '2025-11-08 01:35:00+00:00'),
  ('b2f95613-a6f8-5e35-b6d7-e03bf1cc7aae'::uuid, '187ebbb4-aff9-555e-93e8-84718180c565'::uuid, 'MEMBER', '2025-11-08 01:35:00+00:00', '05a4c217-1f2a-5854-aa76-875725a75a5e'::uuid, '2025-11-08 01:35:00+00:00', '2025-11-08 01:35:00+00:00'),
  ('54505703-ca04-5613-9f4a-d2499f12ee3d'::uuid, '0740e12f-bc1c-556f-9cc7-3ec5332e692e'::uuid, 'OWNER', '2025-11-11 02:20:00+00:00', '47332eb3-b621-5218-a543-df79240c77e9'::uuid, '2025-11-11 02:20:00+00:00', '2025-11-11 02:20:00+00:00'),
  ('54505703-ca04-5613-9f4a-d2499f12ee3d'::uuid, '25a6f954-f1cd-567d-88a0-630c4407b254'::uuid, 'MEMBER', '2025-11-11 02:20:00+00:00', 'c150d962-f99b-5f83-953e-8715650fe5e0'::uuid, '2025-11-11 02:20:00+00:00', '2025-11-11 02:20:00+00:00'),
  ('18525676-8c6b-552b-8de7-a50899ef4b92'::uuid, 'c0445430-562e-5472-bea6-06f3a5d6f645'::uuid, 'OWNER', '2025-11-18 04:05:00+00:00', '036172d2-eb4f-51d5-b91f-bd0ff2cc4a30'::uuid, '2025-11-18 04:05:00+00:00', '2025-11-18 04:05:00+00:00'),
  ('18525676-8c6b-552b-8de7-a50899ef4b92'::uuid, '85651d6b-4cc0-56ba-ba15-ffc404f10abc'::uuid, 'MEMBER', '2025-11-18 04:05:00+00:00', '9d9ec7e0-e622-51e5-bcef-925c75431f6d'::uuid, '2025-11-18 04:05:00+00:00', '2025-11-18 04:05:00+00:00'),
  ('8dfcb679-8243-5be9-b8ee-b2bde7997277'::uuid, '15c1be82-ea36-5205-af17-7fb5947c2027'::uuid, 'OWNER', '2025-12-02 01:50:00+00:00', '6daf50ac-083f-5960-b651-46e383e80453'::uuid, '2025-12-02 01:50:00+00:00', '2025-12-02 01:50:00+00:00'),
  ('8dfcb679-8243-5be9-b8ee-b2bde7997277'::uuid, '729525be-38aa-50fd-8ea9-3fedf76615f1'::uuid, 'MEMBER', '2025-12-02 01:50:00+00:00', '573f762b-4db4-53ea-bb20-db077c82ec2e'::uuid, '2025-12-02 01:50:00+00:00', '2025-12-02 01:50:00+00:00'),
  ('ef1e1ed3-a3b9-5fd0-86a5-2beec97bdf48'::uuid, '4c507932-ae90-57a1-8765-885e45eba112'::uuid, 'OWNER', '2025-12-08 06:05:00+00:00', 'a8a0ecd6-31ee-5f33-b333-59838740d3c7'::uuid, '2025-12-08 06:05:00+00:00', '2025-12-08 06:05:00+00:00'),
  ('ef1e1ed3-a3b9-5fd0-86a5-2beec97bdf48'::uuid, 'c0445430-562e-5472-bea6-06f3a5d6f645'::uuid, 'MEMBER', '2025-12-08 06:05:00+00:00', '670d9866-7d80-5d13-8234-d226400dfc50'::uuid, '2025-12-08 06:05:00+00:00', '2025-12-08 06:05:00+00:00'),
  ('53774151-12ea-53d4-9d34-ebccfd4a2594'::uuid, '85651d6b-4cc0-56ba-ba15-ffc404f10abc'::uuid, 'OWNER', '2025-10-20 01:05:00+00:00', '7c98993f-ee0e-5a1d-8ea6-d3859261598f'::uuid, '2025-10-20 01:05:00+00:00', '2025-10-20 01:05:00+00:00'),
  ('f8c4432f-0252-5275-a581-958039b98639'::uuid, 'e892c55a-77c6-5c8f-8e00-00da20839ba9'::uuid, 'OWNER', '2025-12-15 02:35:00+00:00', 'c2460bb5-0b9f-5e80-bcfc-3c3e58b699fc'::uuid, '2025-12-15 02:35:00+00:00', '2025-12-15 02:35:00+00:00'),
  ('f8c4432f-0252-5275-a581-958039b98639'::uuid, '187ebbb4-aff9-555e-93e8-84718180c565'::uuid, 'MEMBER', '2025-12-15 02:35:00+00:00', 'bd3f7b3d-6ef2-5cb4-a7d0-141693c6cc8d'::uuid, '2025-12-15 02:35:00+00:00', '2025-12-15 02:35:00+00:00'),
  ('6268eced-f86b-5e52-b0a9-262a806879e9'::uuid, '25a6f954-f1cd-567d-88a0-630c4407b254'::uuid, 'OWNER', '2026-01-05 03:05:00+00:00', '28875f6d-1910-5196-90aa-9544cdc604aa'::uuid, '2026-01-05 03:05:00+00:00', '2026-01-05 03:05:00+00:00'),
  ('6268eced-f86b-5e52-b0a9-262a806879e9'::uuid, '4c507932-ae90-57a1-8765-885e45eba112'::uuid, 'MEMBER', '2026-01-05 03:05:00+00:00', '78f81e8d-d5a2-5ba6-a0e7-6339edc67657'::uuid, '2026-01-05 03:05:00+00:00', '2026-01-05 03:05:00+00:00'),
  ('6268eced-f86b-5e52-b0a9-262a806879e9'::uuid, 'a678ac27-3077-5ef2-8919-5218b2e48791'::uuid, 'MEMBER', '2026-01-05 03:05:00+00:00', 'bf434e4f-e1bf-5e50-93b0-8ee0bcd5d014'::uuid, '2026-01-05 03:05:00+00:00', '2026-01-05 03:05:00+00:00'),
  ('144b02e3-6867-41af-b563-096a06fd83e2'::uuid, '00000000-0000-0000-0000-000000000001'::uuid, 'OWNER', '2026-08-16 09:27:57.407833+00:00', '30fda2e6-4593-49a6-8b44-f9d46b737510'::uuid, '2026-08-16 09:27:57.407828+00:00', '2026-08-16 09:27:57.407832+00:00'),
  ('09452af7-3543-42ef-8d8d-439daab81cc7'::uuid, '00000000-0000-0000-0000-000000000001'::uuid, 'OWNER', '2026-08-16 09:38:58.655169+00:00', 'fc99040e-f652-4280-89f8-6f562e299b55'::uuid, '2026-08-16 09:38:58.655162+00:00', '2026-08-16 09:38:58.655167+00:00'),
  ('ae94fe31-2a34-4652-a9ed-03d154eba768'::uuid, '00000000-0000-0000-0000-000000000001'::uuid, 'OWNER', '2026-08-16 09:39:22.005934+00:00', '57451662-f49d-453a-a69a-62558e7399c5'::uuid, '2026-08-16 09:39:22.005929+00:00', '2026-08-16 09:39:22.005932+00:00'),
  ('29e97dc3-2e93-4430-9a12-9b3992541f31'::uuid, '00000000-0000-0000-0000-000000000001'::uuid, 'OWNER', '2026-08-16 09:40:18.609423+00:00', 'f3fe94fb-1b2b-4820-963a-d36016f2783c'::uuid, '2026-08-16 09:40:18.609418+00:00', '2026-08-16 09:40:18.609422+00:00'),
  ('70949b7e-c7ff-43f0-baa9-3932c3dc0ae3'::uuid, '00000000-0000-0000-0000-000000000001'::uuid, 'OWNER', '2026-08-16 09:43:38.562359+00:00', 'c58403dd-e8e8-4cec-bc1d-bdb4d1ee94b7'::uuid, '2026-08-16 09:43:38.562351+00:00', '2026-08-16 09:43:38.562357+00:00'),
  ('669dd2e7-e3f3-4c46-a186-cd5c28f3882f'::uuid, '00000000-0000-0000-0000-000000000001'::uuid, 'OWNER', '2026-08-16 13:05:25.479373+00:00', 'cb95cefe-f434-4d8a-9383-16be68b699df'::uuid, '2026-08-16 13:05:25.478665+00:00', '2026-08-16 13:05:25.478697+00:00'),
  ('ebc843c9-ad12-4e4e-ad45-c38a8057c0fd'::uuid, '00000000-0000-0000-0000-000000000001'::uuid, 'OWNER', '2026-08-16 13:05:32.692537+00:00', '9a1fa216-153a-4a7b-b662-116528560ba9'::uuid, '2026-08-16 13:05:32.692508+00:00', '2026-08-16 13:05:32.692531+00:00'),
  ('91b0cb2c-33af-4ffe-a16c-272b6effce77'::uuid, '00000000-0000-0000-0000-000000000001'::uuid, 'OWNER', '2026-08-16 13:05:33.739769+00:00', 'a0c0c702-0506-4aa9-b339-331926b0339b'::uuid, '2026-08-16 13:05:33.739744+00:00', '2026-08-16 13:05:33.739764+00:00'),
  ('50816322-8cf7-46ff-b3cf-50dac3837609'::uuid, '00000000-0000-0000-0000-000000000001'::uuid, 'OWNER', '2026-08-16 13:06:32.312944+00:00', 'aed704a1-0186-41d2-b417-4afebbf13d63'::uuid, '2026-08-16 13:06:32.312939+00:00', '2026-08-16 13:06:32.312943+00:00'),
  ('0baed64b-d380-4a01-a64b-265af7059568'::uuid, 'a678ac27-3077-5ef2-8919-5218b2e48791'::uuid, 'OWNER', '2026-08-17 09:03:35.793232+00:00', 'efab7948-b227-4402-9acb-51bac540af65'::uuid, '2026-08-17 09:03:35.793224+00:00', '2026-08-17 09:03:35.793229+00:00'),
  ('b05c0f83-d93a-439b-bb1a-f7c109af8201'::uuid, 'a678ac27-3077-5ef2-8919-5218b2e48791'::uuid, 'OWNER', '2026-08-22 02:07:39.153722+00:00', '2417a27b-b289-448b-9f3a-68a772d2a01a'::uuid, '2026-08-22 02:07:39.153712+00:00', '2026-08-22 02:07:39.153718+00:00'),
  ('0772523a-7235-410b-8eea-ee711baa62e0'::uuid, 'a678ac27-3077-5ef2-8919-5218b2e48791'::uuid, 'OWNER', '2026-08-22 09:52:25.609677+00:00', '809173ae-8d70-4532-9d79-3464e6eb336e'::uuid, '2026-08-22 09:52:25.609669+00:00', '2026-08-22 09:52:25.609674+00:00'),
  ('2da8c727-32f8-4ce2-9528-ae87ee60077d'::uuid, '01b19ecb-53ef-4373-99a5-3b0d8bd3af61'::uuid, 'OWNER', '2026-08-23 12:15:53.251748+00:00', 'f666dffe-bac2-48af-bae1-f488a77527c9'::uuid, '2026-08-23 12:15:53.251739+00:00', '2026-08-23 12:15:53.251745+00:00'),
  ('c6e50b32-d59d-41d5-b634-618d8a4286c8'::uuid, '01b19ecb-53ef-4373-99a5-3b0d8bd3af61'::uuid, 'OWNER', '2026-08-24 08:57:35.840017+00:00', '2c558c6c-07c1-42e2-986b-29c8826d93e4'::uuid, '2026-08-24 08:57:35.840004+00:00', '2026-08-24 08:57:35.840013+00:00')
ON CONFLICT DO NOTHING;

-- Data for: requirements (31 rows)
INSERT INTO "requirements" ("project_id", "type", "title", "description", "priority", "id", "created_at", "updated_at") VALUES
  ('7e621a51-f48a-53bf-927d-f415ae6c9249'::uuid, 'BUSINESS', 'Theo dõi hiệu quả vận hành kho lưu trữ hồ sơ bệnh án', 'Ban giám đốc bệnh viện cần nắm được tình hình lưu trữ hồ sơ bệnh án trên toàn viện: số lượng hồ sơ đang lưu trữ, tỷ lệ lấp đầy kho/tủ/ngăn, và tốc độ xử lý hồ sơ mượn/trả để lập kế hoạch mở rộng kho lưu trữ.', 'HIGH', '570cecdf-7f76-54ed-8375-c59446c6b4ec'::uuid, '2025-11-05 02:30:00+00:00', '2025-11-05 02:30:00+00:00'),
  ('7e621a51-f48a-53bf-927d-f415ae6c9249'::uuid, 'ANALYTICAL', 'Phân tích số lượng hồ sơ lưu trữ theo khoa và theo tháng', 'Cần thống kê số lượng hồ sơ bệnh án được đưa vào lưu trữ theo từng khoa (Vào từ khoa/Ra từ khoa) và theo từng tháng để phát hiện khoa nào phát sinh nhiều hồ sơ lưu trữ nhất.', 'HIGH', 'ef41f280-58cb-591e-b632-d91f33c11383'::uuid, '2025-11-06 03:00:00+00:00', '2025-11-06 03:00:00+00:00'),
  ('7e621a51-f48a-53bf-927d-f415ae6c9249'::uuid, 'ANALYTICAL', 'Phân tích tỷ lệ lấp đầy Kho - Tủ - Ngăn', 'Cần tính tỷ lệ lấp đầy (số hồ sơ / sức chứa) của từng Kho, từng Tủ và từng Ngăn để cảnh báo khi gần đầy, hỗ trợ điều phối vị trí lưu trữ mới.', 'MEDIUM', '8859e59b-6215-5416-ae06-8c8fd5e674a7'::uuid, '2025-11-07 01:20:00+00:00', '2025-11-07 01:20:00+00:00'),
  ('7e621a51-f48a-53bf-927d-f415ae6c9249'::uuid, 'TECHNICAL', 'Ẩn danh hóa dữ liệu định danh bệnh nhân trước khi đưa vào DW', 'Các trường như Họ và tên, Địa chỉ, Số bệnh án phải được ẩn danh hóa (hashing/masking) trước khi lưu vào các bảng fact/dimension công khai cho phân tích, chỉ giữ Số hồ sơ dạng mã hóa để truy vết khi cần.', 'HIGH', '9cc6179c-f4e3-5cb2-a4d0-a71f9c84511d'::uuid, '2025-11-08 07:10:00+00:00', '2025-11-08 07:10:00+00:00'),
  ('84bdeb46-0eba-564e-8437-833ede4e2718'::uuid, 'ANALYTICAL', 'Phân tích lượt khám và chẩn đoán theo khoa/quý', 'Cần đo số lượt bệnh nhân vào viện, ra viện theo từng khoa và từng quý, kèm top 10 chẩn đoán phổ biến nhất để phục vụ báo cáo Sở Y tế.', 'HIGH', 'da3ce17b-dd03-5f74-af74-71ab701a72be'::uuid, '2025-12-11 02:00:00+00:00', '2025-12-11 02:00:00+00:00'),
  ('84bdeb46-0eba-564e-8437-833ede4e2718'::uuid, 'ANALYTICAL', 'Phân tích cơ cấu đối tượng chi trả viện phí', 'Cần tính tỷ lệ bệnh nhân theo đối tượng chi trả (BHYT, BHYT Quân, Viện phí, Dịch vụ, Miễn phí) theo từng khoa và theo thời gian để đánh giá cơ cấu nguồn thu.', 'MEDIUM', 'f9711f5b-fd8f-54db-b376-16b19781095a'::uuid, '2025-12-12 04:15:00+00:00', '2025-12-12 04:15:00+00:00'),
  ('b2f95613-a6f8-5e35-b6d7-e03bf1cc7aae'::uuid, 'ANALYTICAL', 'Phân tích giao dịch bất thường theo khách hàng và thời gian', 'Cần tổng hợp số lượng và giá trị giao dịch theo khách hàng, kênh giao dịch (ATM, Internet Banking, POS) theo từng ngày để phát hiện giao dịch bất thường vượt ngưỡng.', 'HIGH', '19feddd3-2507-545f-ae72-80cb52055602'::uuid, '2025-11-09 02:00:00+00:00', '2025-11-09 02:00:00+00:00'),
  ('b2f95613-a6f8-5e35-b6d7-e03bf1cc7aae'::uuid, 'TECHNICAL', 'Mã hóa số tài khoản và CCCD khách hàng', 'Số tài khoản, số CCCD và số điện thoại khách hàng phải được mã hóa hai chiều (encryption at rest) và chỉ giải mã khi có thẩm quyền truy cập theo quy định bảo mật ngân hàng.', 'HIGH', '18ff1ee9-b7a0-5482-9b94-9716b7baea36'::uuid, '2025-11-10 03:30:00+00:00', '2025-11-10 03:30:00+00:00'),
  ('54505703-ca04-5613-9f4a-d2499f12ee3d'::uuid, 'ANALYTICAL', 'Phân tích doanh thu theo ngành hàng và khu vực', 'Cần tổng hợp doanh thu, số lượng đơn hàng theo ngành hàng, khu vực cửa hàng và theo tuần để xác định ngành hàng tăng trưởng/suy giảm.', 'HIGH', '5595825c-8ac4-5a53-abe1-0f4ca49e76f7'::uuid, '2025-11-12 01:40:00+00:00', '2025-11-12 01:40:00+00:00'),
  ('18525676-8c6b-552b-8de7-a50899ef4b92'::uuid, 'ANALYTICAL', 'Phân tích tỷ lệ giao hàng đúng hạn theo tuyến', 'Cần đo tỷ lệ đơn hàng giao đúng hạn, thời gian trung chuyển trung bình theo từng tuyến vận chuyển và từng đối tác vận chuyển theo tháng.', 'HIGH', 'a4db5a66-b2ad-5171-91d5-401cb72e1bff'::uuid, '2025-11-19 02:30:00+00:00', '2025-11-19 02:30:00+00:00'),
  ('8dfcb679-8243-5be9-b8ee-b2bde7997277'::uuid, 'ANALYTICAL', 'Phân tích tỷ lệ tốt nghiệp theo khoa/ngành', 'Cần thống kê số sinh viên nhập học, số sinh viên tốt nghiệp đúng hạn theo từng khoa/ngành và theo từng khóa học để đánh giá chất lượng đào tạo.', 'MEDIUM', '39163bc9-1fa4-5f99-9b25-68a2b7fff063'::uuid, '2025-12-03 02:00:00+00:00', '2025-12-03 02:00:00+00:00'),
  ('ef1e1ed3-a3b9-5fd0-86a5-2beec97bdf48'::uuid, 'ANALYTICAL', 'Phân tích chỉ số OEE theo dây chuyền sản xuất', 'Cần tính chỉ số OEE (Overall Equipment Effectiveness) theo từng dây chuyền, từng ca sản xuất, bao gồm tỷ lệ khả dụng, hiệu suất và chất lượng.', 'HIGH', 'fe5803e1-db15-5ba3-a81a-32e73a9be9da'::uuid, '2025-12-09 01:15:00+00:00', '2025-12-09 01:15:00+00:00'),
  ('53774151-12ea-53d4-9d34-ebccfd4a2594'::uuid, 'ANALYTICAL', 'Phân tích tỷ lệ bồi thường theo sản phẩm bảo hiểm', 'Cần tính tỷ lệ claim được duyệt/từ chối theo từng sản phẩm bảo hiểm và theo thời gian để đánh giá mức độ rủi ro của từng dòng sản phẩm.', 'MEDIUM', 'e33ff717-a4cb-5623-a2d1-a84c16a7d4cc'::uuid, '2025-10-21 02:00:00+00:00', '2025-10-21 02:00:00+00:00'),
  ('f8c4432f-0252-5275-a581-958039b98639'::uuid, 'ANALYTICAL', 'Phân tích tỷ lệ rời mạng (churn) theo gói cước', 'Cần dự báo tỷ lệ thuê bao rời mạng theo từng gói cước, khu vực và theo tháng dựa trên lịch sử sử dụng lưu lượng và doanh thu ARPU.', 'HIGH', '056a6dd6-4c2d-57ca-83cc-cff6822d284d'::uuid, '2025-12-16 03:00:00+00:00', '2025-12-16 03:00:00+00:00'),
  ('6268eced-f86b-5e52-b0a9-262a806879e9'::uuid, 'ANALYTICAL', 'Phân tích tỷ lệ bỏ giỏ hàng và hiệu quả kênh marketing', 'Cần đo tỷ lệ bỏ giỏ hàng theo từng danh mục sản phẩm, và hiệu quả chuyển đổi của từng kênh marketing (Facebook Ads, Google Ads, Email) theo tuần.', 'HIGH', '3ae76b93-52e4-5755-afe1-cae0085d4c97'::uuid, '2026-01-06 02:30:00+00:00', '2026-01-06 02:30:00+00:00'),
  ('0772523a-7235-410b-8eea-ee711baa62e0'::uuid, 'BUSINESS', 'Quản lý vị trí và trạng thái lưu trữ hồ sơ bệnh án', 'Quản lý chi tiết vị trí vật lý lưu trữ hồ sơ bệnh án (Kho, Tủ, Ngăn, Kệ, Ký hiệu) và trạng thái hồ sơ (đang lưu trữ, chờ đưa vào kho, cần bổ sung xét nghiệm) nhằm phục vụ tra cứu nhanh thông tin bệnh nhân.', 'HIGH', 'f40c11b1-c9de-45df-b7af-c7a86e4836d1'::uuid, '2026-08-22 11:09:22.256827+00:00', '2026-08-22 11:09:22.256830+00:00'),
  ('0772523a-7235-410b-8eea-ee711baa62e0'::uuid, 'ANALYTICAL', 'Phân tích thời gian điều trị trung bình', 'Thống kê và phân tích thời gian điều trị trung bình tính bằng số ngày từ khi vào viện đến khi ra viện, phân theo khoa vào viện, khoa ra viện, nhóm tuổi và giới tính.', 'HIGH', '4189b4d1-fcaa-4576-b774-cda6bebd548b'::uuid, '2026-08-22 11:09:22.256873+00:00', '2026-08-22 11:09:22.256873+00:00'),
  ('0772523a-7235-410b-8eea-ee711baa62e0'::uuid, 'ANALYTICAL', 'Phân tích cơ cấu bệnh nhân tiếp nhận', 'Thống kê số lượng bệnh nhân tiếp nhận theo từng diện đối tượng chi trả (BHYT, BHYT Quân, Miễn phí, Dịch vụ) và loại hình điều trị (Nội trú, Ngoại trú).', 'HIGH', 'bae9ce8c-cd48-47bc-bf33-1cb4ea55a458'::uuid, '2026-08-22 11:09:22.256896+00:00', '2026-08-22 11:09:22.256897+00:00'),
  ('0772523a-7235-410b-8eea-ee711baa62e0'::uuid, 'ANALYTICAL', 'Thống kê hồ sơ bệnh án lưu trữ theo vị trí và trạng thái', 'Thống kê số lượng hồ sơ bệnh án lưu trữ phân chia theo từng trạng thái hồ sơ và vị trí lưu trữ vật lý (Kho, Tủ, Ngăn, Kệ).', 'MEDIUM', 'ce109e4a-6d83-4cb4-9f88-11bd13da074e'::uuid, '2026-08-22 11:09:22.256912+00:00', '2026-08-22 11:09:22.256913+00:00'),
  ('0772523a-7235-410b-8eea-ee711baa62e0'::uuid, 'TECHNICAL', 'Ẩn danh thông tin cá nhân bệnh nhân (PII Protection)', 'Thực hiện ẩn danh các thông tin cá nhân nhạy cảm của bệnh nhân như Họ và tên, Địa chỉ chi tiết thông qua API PII Guard.', 'HIGH', 'c0136892-2be4-492d-84d6-a471142d5dee'::uuid, '2026-08-22 11:09:22.256925+00:00', '2026-08-22 11:09:22.256926+00:00'),
  ('0772523a-7235-410b-8eea-ee711baa62e0'::uuid, 'TECHNICAL', 'Sử dụng khóa thay thế (Surrogate Keys) trong Data Warehouse', 'Toàn bộ các bảng Fact và Dimension trong Data Warehouse phải áp dụng Surrogate Key kiểu số nguyên hoặc UUID thay vì sử dụng trực tiếp số hồ sơ y tế.', 'HIGH', '0e19722d-4e9f-4b31-b958-148f724d9d41'::uuid, '2026-08-22 11:09:22.256938+00:00', '2026-08-22 11:09:22.256939+00:00'),
  ('0772523a-7235-410b-8eea-ee711baa62e0'::uuid, 'TECHNICAL', 'Chuẩn hóa mô hình kho dữ liệu theo Star Schema', 'Thiết kế Data Warehouse theo mô hình hình sao (Star Schema) tối ưu cho các truy vấn OLAP và thiết lập liên kết khóa ngoại rõ ràng.', 'HIGH', '22baad51-402a-4f56-8664-3f3de54b85bc'::uuid, '2026-08-22 11:09:22.256949+00:00', '2026-08-22 11:09:22.256950+00:00'),
  ('2da8c727-32f8-4ce2-9528-ae87ee60077d'::uuid, 'BUSINESS', 'Quản lý vị trí và trạng thái hồ sơ bệnh án', 'Quản lý vị trí vật lý lưu trữ hồ sơ bệnh án (theo Kho, Tủ, Ngăn, Kệ, Ký hiệu) và trạng thái hồ sơ (đang lưu trữ, chờ đưa vào kho, cần bổ sung xét nghiệm) để phục vụ tra cứu nhanh thông tin.', 'HIGH', 'e306cb9c-4abc-49be-a014-ab8feaffd5a9'::uuid, '2026-08-23 12:23:00.644706+00:00', '2026-08-23 12:23:00.644710+00:00'),
  ('2da8c727-32f8-4ce2-9528-ae87ee60077d'::uuid, 'ANALYTICAL', 'Phân tích tình hình khám chữa bệnh và thời gian điều trị', 'Theo dõi số lượng bệnh nhân và thời gian điều trị trung bình (tính từ thời gian vào viện đến ngày ra viện) phân theo khoa vào viện, khoa ra viện, nhóm tuổi và giới tính.', 'HIGH', 'a78f8632-e864-447d-82fc-1f1e05aa18ee'::uuid, '2026-08-23 12:23:00.644751+00:00', '2026-08-23 12:23:00.644752+00:00'),
  ('2da8c727-32f8-4ce2-9528-ae87ee60077d'::uuid, 'ANALYTICAL', 'Thống kê cơ cấu bệnh nhân tiếp nhận', 'Thống kê số lượng và cơ cấu bệnh nhân theo diện đối tượng chi trả (BHYT, BHYT Quân, Miễn phí, Dịch vụ) và loại hình điều trị (Nội trú, Ngoại trú).', 'HIGH', 'efc7c4ce-e5b3-4902-8c2e-2161280f21ee'::uuid, '2026-08-23 12:23:00.644774+00:00', '2026-08-23 12:23:00.644775+00:00'),
  ('2da8c727-32f8-4ce2-9528-ae87ee60077d'::uuid, 'ANALYTICAL', 'Thống kê hồ sơ lưu trữ theo trạng thái và vị trí', 'Thống kê số lượng hồ sơ lưu trữ phân theo trạng thái hồ sơ và vị trí vật lý (Kho, Tủ, Ngăn, Kệ).', 'MEDIUM', 'ff11f830-a869-4f79-9f52-f97229a0a9b6'::uuid, '2026-08-23 12:23:00.644791+00:00', '2026-08-23 12:23:00.644792+00:00'),
  ('2da8c727-32f8-4ce2-9528-ae87ee60077d'::uuid, 'TECHNICAL', 'Bảo mật và ẩn danh thông tin cá nhân (PII)', 'Ẩn danh các thông tin cá nhân của bệnh nhân (Họ và tên, Địa chỉ chi tiết) thông qua PII Guard API.', 'HIGH', 'e4b56c29-9545-4b0b-ac8d-5e407af582e2'::uuid, '2026-08-23 12:23:00.644808+00:00', '2026-08-23 12:23:00.644809+00:00'),
  ('2da8c727-32f8-4ce2-9528-ae87ee60077d'::uuid, 'TECHNICAL', 'Sử dụng khóa thay thế (Surrogate Keys)', 'Sử dụng Surrogate Key dạng số nguyên hoặc UUID cho toàn bộ các bảng Fact và Dimension trong Data Warehouse thay vì dùng trực tiếp số hồ sơ y tế.', 'HIGH', '1e102e88-b39c-4640-9e47-0994b0ad0e0c'::uuid, '2026-08-23 12:23:00.644824+00:00', '2026-08-23 12:23:00.644825+00:00'),
  ('2da8c727-32f8-4ce2-9528-ae87ee60077d'::uuid, 'TECHNICAL', 'Thiết kế mô hình dữ liệu Star Schema', 'Chuẩn hóa và thiết kế Kho dữ liệu theo mô hình hình sao (Star Schema) tối ưu cho các truy vấn OLAP với liên kết khóa ngoại rõ ràng.', 'HIGH', 'd6cde519-7f52-496f-a4be-f845af7e5129'::uuid, '2026-08-23 12:23:00.644838+00:00', '2026-08-23 12:23:00.644839+00:00'),
  ('c6e50b32-d59d-41d5-b634-618d8a4286c8'::uuid, 'BUSINESS', 'Quản lý tình hình bán thuốc và cấp phát đơn thuốc', 'Bệnh viện cần hệ thống Data Warehouse để quản lý và theo dõi tình hình bán thuốc cùng quá trình cấp phát đơn thuốc.', 'HIGH', 'f40a1b92-649e-4330-abac-6273aaea1efa'::uuid, '2026-08-24 16:07:26.774917+00:00', '2026-08-24 16:07:26.774921+00:00'),
  ('c6e50b32-d59d-41d5-b634-618d8a4286c8'::uuid, 'ANALYTICAL', 'Phân tích doanh thu, số lượng cấp phát và thời gian chờ', 'Hệ thống cần đo lường tổng doanh thu, số lượng thuốc đã phát và thời gian chờ nhận thuốc của bệnh nhân, hỗ trợ phân tích chi tiết theo từng loại thuốc và từng đối tượng bệnh nhân.', 'HIGH', 'e8c8d3ce-79df-4b33-bdba-a657de90e011'::uuid, '2026-08-24 16:07:26.774964+00:00', '2026-08-24 16:07:26.774965+00:00')
ON CONFLICT DO NOTHING;

-- Data for: analytical_requirements (19 rows)
INSERT INTO "analytical_requirements" ("requirement_id", "metric", "dimension", "time_granularity", "aggregation_method", "grain", "id", "created_at", "updated_at") VALUES
  ('ef41f280-58cb-591e-b632-d91f33c11383'::uuid, 'Số lượng hồ sơ lưu trữ', 'Khoa (vào/ra)', 'Tháng', 'COUNT', 'Mỗi dòng = 1 hồ sơ lưu trữ, nhóm theo khoa và tháng lưu trữ', 'b0c6889c-f3f5-5bed-a0d3-13b3490c4767'::uuid, '2025-11-06 03:00:00+00:00', '2025-11-06 03:00:00+00:00'),
  ('8859e59b-6215-5416-ae06-8c8fd5e674a7'::uuid, 'Tỷ lệ lấp đầy vị trí lưu trữ', 'Kho, Tủ, Ngăn', 'Ngày', 'AVG', 'Mỗi dòng = 1 vị trí lưu trữ (ngăn), tính theo số hồ sơ hiện có / sức chứa tại thời điểm snapshot theo ngày', '264ef9be-4fea-52bc-a117-99a6eb7f8f47'::uuid, '2025-11-07 01:20:00+00:00', '2025-11-07 01:20:00+00:00'),
  ('da3ce17b-dd03-5f74-af74-71ab701a72be'::uuid, 'Số lượt khám bệnh', 'Khoa, Chẩn đoán', 'Quý', 'COUNT', 'Mỗi dòng = 1 lượt vào/ra viện của bệnh nhân, nhóm theo khoa và quý', 'ad73c3b5-3fec-5dca-b11d-d32a29c6e42c'::uuid, '2025-12-11 02:00:00+00:00', '2025-12-11 02:00:00+00:00'),
  ('f9711f5b-fd8f-54db-b376-16b19781095a'::uuid, 'Số bệnh nhân theo đối tượng chi trả', 'Đối tượng chi trả, Khoa', 'Quý', 'COUNT', 'Mỗi dòng = 1 bệnh án, nhóm theo đối tượng chi trả và khoa', '90b35778-8996-555d-8e8f-6087150cece1'::uuid, '2025-12-12 04:15:00+00:00', '2025-12-12 04:15:00+00:00'),
  ('19feddd3-2507-545f-ae72-80cb52055602'::uuid, 'Giá trị & số lượng giao dịch', 'Khách hàng, Kênh giao dịch', 'Ngày', 'SUM', 'Mỗi dòng = 1 giao dịch, nhóm theo khách hàng, kênh và ngày giao dịch', '087343bc-acb7-5ffb-8ebb-5e414c8d384a'::uuid, '2025-11-09 02:00:00+00:00', '2025-11-09 02:00:00+00:00'),
  ('5595825c-8ac4-5a53-abe1-0f4ca49e76f7'::uuid, 'Doanh thu bán hàng', 'Ngành hàng, Khu vực', 'Tuần', 'SUM', 'Mỗi dòng = 1 dòng hóa đơn bán hàng (order line), nhóm theo ngành hàng, khu vực và tuần', 'e2733ad8-c03e-5157-a74c-3761efb09725'::uuid, '2025-11-12 01:40:00+00:00', '2025-11-12 01:40:00+00:00'),
  ('a4db5a66-b2ad-5171-91d5-401cb72e1bff'::uuid, 'Tỷ lệ giao hàng đúng hạn', 'Tuyến vận chuyển, Đối tác', 'Tháng', 'AVG', 'Mỗi dòng = 1 vận đơn, nhóm theo tuyến vận chuyển, đối tác vận chuyển và tháng giao hàng', 'e2b336b4-29cf-5489-80df-d6cd31f0dd9a'::uuid, '2025-11-19 02:30:00+00:00', '2025-11-19 02:30:00+00:00'),
  ('39163bc9-1fa4-5f99-9b25-68a2b7fff063'::uuid, 'Tỷ lệ tốt nghiệp', 'Khoa/Ngành, Khóa học', 'Năm học', 'AVG', 'Mỗi dòng = 1 sinh viên, nhóm theo khoa/ngành và khóa học nhập học', 'c46f00d2-dcfa-52c9-9b8d-164db566ee24'::uuid, '2025-12-03 02:00:00+00:00', '2025-12-03 02:00:00+00:00'),
  ('fe5803e1-db15-5ba3-a81a-32e73a9be9da'::uuid, 'Chỉ số OEE', 'Dây chuyền, Ca sản xuất', 'Ca', 'AVG', 'Mỗi dòng = 1 ca sản xuất trên 1 dây chuyền, tính OEE = Availability x Performance x Quality', '346bc6a6-c524-5a2d-8e44-07f48f07fa1d'::uuid, '2025-12-09 01:15:00+00:00', '2025-12-09 01:15:00+00:00'),
  ('e33ff717-a4cb-5623-a2d1-a84c16a7d4cc'::uuid, 'Tỷ lệ bồi thường', 'Sản phẩm bảo hiểm', 'Tháng', 'AVG', 'Mỗi dòng = 1 hồ sơ yêu cầu bồi thường (claim), nhóm theo sản phẩm bảo hiểm và tháng phát sinh', '156c0f5e-1958-5d67-a88a-a8c4d081fc0f'::uuid, '2025-10-21 02:00:00+00:00', '2025-10-21 02:00:00+00:00'),
  ('056a6dd6-4c2d-57ca-83cc-cff6822d284d'::uuid, 'Tỷ lệ rời mạng', 'Gói cước, Khu vực', 'Tháng', 'AVG', 'Mỗi dòng = 1 thuê bao đang hoạt động, nhóm theo gói cước, khu vực và tháng quan sát', 'a0059bf6-b64d-580e-a847-313493ab2160'::uuid, '2025-12-16 03:00:00+00:00', '2025-12-16 03:00:00+00:00'),
  ('3ae76b93-52e4-5755-afe1-cae0085d4c97'::uuid, 'Tỷ lệ bỏ giỏ hàng & hiệu quả marketing', 'Danh mục sản phẩm, Kênh marketing', 'Tuần', 'AVG', 'Mỗi dòng = 1 phiên mua sắm (session), nhóm theo danh mục sản phẩm, kênh marketing và tuần', '1a650908-3f52-5126-89e7-7ac7cd3475f8'::uuid, '2026-01-06 02:30:00+00:00', '2026-01-06 02:30:00+00:00'),
  ('4189b4d1-fcaa-4576-b774-cda6bebd548b'::uuid, 'Thời gian điều trị trung bình', 'Vào từ khoa, Ra từ khoa, Tuổi, Giới', 'Day', 'AVG', 'Lượt điều trị', '0a90bf0e-398a-4ea7-81d7-b4cb5788a325'::uuid, '2026-08-22 11:09:44.449359+00:00', '2026-08-22 11:09:44.449363+00:00'),
  ('bae9ce8c-cd48-47bc-bf33-1cb4ea55a458'::uuid, 'Số lượng bệnh nhân tiếp nhận', 'Đối tượng, Loại', 'None', 'COUNT_DISTINCT', 'Bệnh nhân', '41026a9a-e4e0-4a58-982e-fb9ef3eae55b'::uuid, '2026-08-22 11:09:44.449383+00:00', '2026-08-22 11:09:44.449384+00:00'),
  ('ce109e4a-6d83-4cb4-9f88-11bd13da074e'::uuid, 'Số lượng hồ sơ bệnh án lưu trữ', 'Trạng thái hồ sơ, Kho, Tủ, Ngăn, Vị trí', 'None', 'COUNT', 'Hồ sơ bệnh án', '0b6b41b2-fc18-4565-9252-de0dbf9da7a7'::uuid, '2026-08-22 11:09:44.449394+00:00', '2026-08-22 11:09:44.449394+00:00'),
  ('a78f8632-e864-447d-82fc-1f1e05aa18ee'::uuid, 'Số lượng bệnh nhân', 'Vào từ khoa, Ra từ khoa, Tuổi, Giới', 'Ngày', 'COUNT', 'Bệnh nhân', '172f883b-52e4-4d50-b06f-72555bc66d0b'::uuid, '2026-08-23 12:23:26.304300+00:00', '2026-08-23 12:23:26.304306+00:00'),
  ('a78f8632-e864-447d-82fc-1f1e05aa18ee'::uuid, 'Thời gian điều trị trung bình', 'Vào từ khoa, Ra từ khoa, Tuổi, Giới', 'Ngày', 'AVG', 'Lượt điều trị', '65e200e7-0f93-4768-8392-0061b5cd7fb9'::uuid, '2026-08-23 12:23:26.304347+00:00', '2026-08-23 12:23:26.304348+00:00'),
  ('efc7c4ce-e5b3-4902-8c2e-2161280f21ee'::uuid, 'Số lượng bệnh nhân', 'Đối tượng, Loại', 'Tháng', 'COUNT', 'Bệnh nhân', '779095c8-a96a-443e-bd2d-2b83237fd0c1'::uuid, '2026-08-23 12:23:26.304376+00:00', '2026-08-23 12:23:26.304377+00:00'),
  ('ff11f830-a869-4f79-9f52-f97229a0a9b6'::uuid, 'Số lượng hồ sơ lưu trữ', 'Trạng thái hồ sơ, Kho, Tủ, Ngăn, Vị trí', 'Ngày', 'COUNT', 'Hồ sơ', '65325e55-5e26-43e8-9b01-a541d08140e9'::uuid, '2026-08-23 12:23:26.304397+00:00', '2026-08-23 12:23:26.304398+00:00')
ON CONFLICT DO NOTHING;

-- Data for: data_sources (39 rows)
INSERT INTO "data_sources" ("project_id", "name", "type", "description", "location", "schema_metadata", "id", "created_at", "updated_at") VALUES
  ('2da8c727-32f8-4ce2-9528-ae87ee60077d'::uuid, 'DanhSachBenhNhan.csv', 'CSV', NULL, 'D:/VinAI/P-102/backend/data/uploads/2da8c727-32f8-4ce2-9528-ae87ee60077d/DanhSachBenhNhan.csv', '{"tables": [{"name": "DanhSachBenhNhan", "columns": [{"name": "Số hồ sơ", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": true, "is_unique_candidate": true}, {"name": "Số lưu trữ", "nullable": false, "data_type": "INTEGER", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Tên bệnh nhân", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Tuổi", "nullable": false, "data_type": "INTEGER", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 11, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Giới", "nullable": false, "data_type": "CATEGORY", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 2, "distinct_values": ["Nam", "Nữ"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Địa chỉ", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Thời gian vào viện", "nullable": false, "data_type": "DATETIME", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Ngày ra", "nullable": false, "data_type": "DATETIME", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Vào từ khoa", "nullable": false, "data_type": "CATEGORY", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 8, "distinct_values": ["Khoa A7 (Nội thận - Tiết niệu)", "Khoa B9 (Tai - Mũi - Họng)", "Khoa A2 (Chấn thương chỉnh hình)", "Khoa A16 (Quốc tế)", "Khoa Khám bệnh", "Khoa Xạ trị", "Khoa B1-A (CT-Can thiệp)", "Khoa A1 (Nội tổng hợp)"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Ra từ khoa", "nullable": false, "data_type": "CATEGORY", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 8, "distinct_values": ["Khoa A7 (Nội thận - Tiết niệu)", "Khoa B9 (Tai - Mũi - Họng)", "Khoa A2 (Chấn thương chỉnh hình)", "Khoa Khám bệnh", "Khoa A16 (Quốc tế)", "Khoa B6 (Ngoại chấn thương)", "Khoa Xạ trị", "Khoa B1-A (CT-Can thiệp)"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Chẩn đoán", "nullable": false, "data_type": "CATEGORY", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 6, "distinct_values": ["Nhồi máu cơ tim cấp", "Thoát vị đĩa đệm cột sống thắt lưng", "Sỏi thận", "Đái tháo đường type 2", "Viêm xoang mạn tính", "U xơ tử cung"], "is_key_candidate": false, "is_unique_candidate": false}]}], "relationships": []}', 'db04181c-0f1b-42da-a64b-fa91247a6201'::uuid, '2026-08-23 12:17:44.462077+00:00', '2026-08-23 12:22:38.321022+00:00'),
  ('7e621a51-f48a-53bf-927d-f415ae6c9249'::uuid, 'VIMES - Danh mục dùng chung (Master Data)', 'EXCEL', 'File Excel mô tả cấu trúc dữ liệu và danh mục dùng chung (Giới tính, Khoa, Đối tượng, Trạng thái hồ sơ, Kho/Tủ/Ngăn) do phòng CNTT bệnh viện cung cấp.', '/uploads/vimes/VIMES_Patient_Record_Cau_truc_du_lieu_2.xlsx', '{"note": "Ánh xạ trực tiếp từ sheet ''5.Danh muc (Master Data)'' trong tài liệu cấu trúc dữ liệu VIMES do người dùng cung cấp. Đã bổ sung đầy đủ 9 danh mục (trước đó chỉ có 4/9) và đầy đủ toàn bộ mã khoa (14/14) thay vì chỉ trích mẫu.", "tables": [{"name": "dm_gioi_tinh", "columns": [{"name": "ma", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "ten_hien_thi", "data_type": "TEXT", "constraints": [], "distinct_values": []}], "description": "Danh mục giới tính. Áp dụng cho trường Giới (Sheet 1, Sheet 4) / Giới tính (Sheet 2)", "sample_rows": [{"ma": "1", "ten_hien_thi": "Nam"}, {"ma": "2", "ten_hien_thi": "Nữ"}]}, {"name": "dm_khoa", "note": "Danh sách khoa chỉ là ví dụ minh họa; cần đối chiếu danh mục khoa thực tế của bệnh viện trước khi đưa vào CSDL chính thức.", "columns": [{"name": "ma_khoa", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "ten_khoa", "data_type": "TEXT", "constraints": [], "distinct_values": []}], "description": "Danh mục khoa/phòng bệnh viện. Áp dụng cho trường Vào từ khoa / Ra từ khoa (Sheet 1, Sheet 3, Sheet 4)", "sample_rows": [{"ma_khoa": "A1", "ten_khoa": "Khoa A1 - Nội tổng hợp"}, {"ma_khoa": "A2", "ten_khoa": "Khoa A2 - Chấn thương chỉnh hình"}, {"ma_khoa": "A6", "ten_khoa": "Khoa A6 - Huyết học lâm sàng"}, {"ma_khoa": "A7", "ten_khoa": "Khoa A7 - Nội thận - Tiết niệu"}, {"ma_khoa": "A8", "ten_khoa": "Khoa A8 - Da liễu"}, {"ma_khoa": "A15", "ten_khoa": "Khoa A15 - Nội tổng hợp"}, {"ma_khoa": "A16", "ten_khoa": "Khoa A16 - Quốc tế"}, {"ma_khoa": "B1-A", "ten_khoa": "Khoa B1-A - Chẩn đoán hình ảnh (CT-Can thiệp)"}, {"ma_khoa": "B1-C", "ten_khoa": "Khoa B1-C - Phẫu thuật"}, {"ma_khoa": "B3", "ten_khoa": "Khoa B3 - Ngoại tổng hợp"}, {"ma_khoa": "B6", "ten_khoa": "Khoa B6 - Ngoại chấn thương"}, {"ma_khoa": "B9", "ten_khoa": "Khoa B9 - Tai - Mũi - Họng"}, {"ma_khoa": "XT", "ten_khoa": "Khoa Xạ trị"}, {"ma_khoa": "KB", "ten_khoa": "Khoa Khám bệnh"}]}, {"name": "dm_doi_tuong", "columns": [{"name": "ma", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "ten_hien_thi", "data_type": "TEXT", "constraints": [], "distinct_values": []}], "description": "Danh mục đối tượng chi trả viện phí. Áp dụng cho trường Đối tượng (Sheet 2)", "sample_rows": [{"ma": "BHYT", "ten_hien_thi": "BHYT"}, {"ma": "BHYT_QUAN", "ten_hien_thi": "BHYT Quân"}, {"ma": "VP", "ten_hien_thi": "Viện phí (Tự trả)"}, {"ma": "DV", "ten_hien_thi": "Dịch vụ"}, {"ma": "MP", "ten_hien_thi": "Miễn phí"}]}, {"name": "dm_loai_benh_an", "columns": [{"name": "ma", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "ten_hien_thi", "data_type": "TEXT", "constraints": [], "distinct_values": []}], "description": "Danh mục loại bệnh án. Áp dụng cho trường Loại (Sheet 2)", "sample_rows": [{"ma": "NGT", "ten_hien_thi": "Bệnh án điều trị ngoại trú"}, {"ma": "NOI", "ten_hien_thi": "Bệnh án điều trị nội trú"}]}, {"name": "dm_trang_thai_ho_so", "columns": [{"name": "ma", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "ten_hien_thi", "data_type": "TEXT", "constraints": [], "distinct_values": []}], "description": "Danh mục trạng thái hồ sơ lưu trữ. Áp dụng cho trường Trạng thái hồ sơ (Sheet 3)", "sample_rows": [{"ma": "DLT", "ten_hien_thi": "Hồ sơ đang lưu trữ"}, {"ma": "DM", "ten_hien_thi": "Hồ sơ đang mượn"}, {"ma": "CDH", "ten_hien_thi": "Hồ sơ chờ đưa vào kho"}, {"ma": "DH", "ten_hien_thi": "Hồ sơ đã hủy"}]}, {"name": "dm_kho", "columns": [{"name": "ma", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "ten_hien_thi", "data_type": "TEXT", "constraints": [], "distinct_values": []}], "description": "Danh mục kho lưu trữ. Áp dụng cho trường Kho (Sheet 3). Quan hệ phân cấp: Kho (1) - Tủ (n) - Ngăn (n), mỗi Tủ thuộc 1 Kho, mỗi Ngăn thuộc 1 Tủ.", "sample_rows": [{"ma": "K1", "ten_hien_thi": "Kho 1"}, {"ma": "K2", "ten_hien_thi": "Kho 2"}, {"ma": "K3", "ten_hien_thi": "Kho 3"}]}, {"name": "dm_tu", "columns": [{"name": "ma", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "kho_ma", "data_type": "TEXT", "constraints": [], "foreign_key": {"references": "dm_kho.ma"}, "distinct_values": []}, {"name": "ten_hien_thi", "data_type": "TEXT", "constraints": [], "distinct_values": []}], "description": "Danh mục tủ lưu trữ, mỗi tủ thuộc 1 kho. Áp dụng cho trường Tủ (Sheet 3)", "sample_rows": [{"ma": "T-K1-A", "ten_hien_thi": "Tủ A (thuộc Kho 1)"}, {"ma": "T-K1-B", "ten_hien_thi": "Tủ B (thuộc Kho 1)"}, {"ma": "T-K2-A", "ten_hien_thi": "Tủ A (thuộc Kho 2)"}]}, {"name": "dm_ngan", "columns": [{"name": "ma", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "tu_ma", "data_type": "TEXT", "constraints": [], "foreign_key": {"references": "dm_tu.ma"}, "distinct_values": []}, {"name": "ten_hien_thi", "data_type": "TEXT", "constraints": [], "distinct_values": []}], "description": "Danh mục ngăn lưu trữ, mỗi ngăn thuộc 1 tủ. Áp dụng cho trường Ngăn (Sheet 3)", "sample_rows": [{"ma": "N-TA-1", "ten_hien_thi": "Ngăn 1 (thuộc Tủ A)"}, {"ma": "N-TA-2", "ten_hien_thi": "Ngăn 2 (thuộc Tủ A)"}, {"ma": "N-TA-3", "ten_hien_thi": "Ngăn 3 (thuộc Tủ A)"}]}, {"name": "dm_nghe_nghiep", "columns": [{"name": "ma", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "ten_hien_thi", "data_type": "TEXT", "constraints": [], "distinct_values": []}], "description": "Danh mục nghề nghiệp (tùy chọn, có thể để dạng Text tự do). Áp dụng cho trường Nghề nghiệp (Sheet 2)", "sample_rows": [{"ma": "BD", "ten_hien_thi": "Bộ đội"}, {"ma": "CNVC", "ten_hien_thi": "Cán bộ - công chức - viên chức"}, {"ma": "CN", "ten_hien_thi": "Công nhân"}, {"ma": "ND", "ten_hien_thi": "Nông dân"}, {"ma": "HSSV", "ten_hien_thi": "Học sinh - Sinh viên"}, {"ma": "HT", "ten_hien_thi": "Hưu trí"}, {"ma": "TD", "ten_hien_thi": "Tự do"}, {"ma": "K", "ten_hien_thi": "Khác"}]}], "source_system": "VIMES - Danh mục dùng chung (Master Data)"}', '6c568dc6-50ba-5919-8086-31e12eb53326'::uuid, '2025-11-04 02:20:00+00:00', '2025-11-04 02:20:00+00:00'),
  ('84bdeb46-0eba-564e-8437-833ede4e2718'::uuid, 'VIMES Patient Record - Lượt khám & chẩn đoán', 'SQL', 'Trích xuất bảng lượt khám, chẩn đoán ICD-10 và đối tượng chi trả từ hệ thống VIMES cho mục đích phân tích lượt khám.', 'sqlserver://vimes-prod-replica.hospital.local:1433/VIMES_PatientRecord', '{"tables": [{"name": "ho_so_luu_tru", "columns": [{"name": "so_benh_an", "note": "Định dạng NGTBD-nnn hoặc NOI-nnn, duy nhất theo đợt điều trị", "required": true, "data_type": "TEXT", "constraints": [], "primary_key": true, "distinct_values": []}, {"name": "so_ho_so", "required": true, "data_type": "INTEGER", "constraints": [], "foreign_key": {"references": "danh_sach_benh_nhan.so_ho_so"}, "distinct_values": []}, {"name": "thoi_gian_vao_vien", "required": true, "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "ngay_ra_vien", "note": ">= thoi_gian_vao_vien nếu có", "required": false, "data_type": "DATE", "constraints": [], "distinct_values": []}, {"name": "khoa_vao_ma", "required": true, "data_type": "TEXT", "constraints": [], "foreign_key": {"references": "dm_khoa.ma_khoa"}, "distinct_values": []}, {"name": "khoa_ra_ma", "required": true, "data_type": "TEXT", "constraints": [], "foreign_key": {"references": "dm_khoa.ma_khoa"}, "distinct_values": []}, {"name": "chan_doan", "required": false, "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "so_luu_tru", "note": "Duy nhất trong phạm vi kho lưu trữ", "required": true, "data_type": "INTEGER", "constraints": [], "primary_key": false, "distinct_values": []}, {"name": "ngay_luu_tru", "note": ">= ngay_ra_vien", "required": true, "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "trang_thai_ho_so_ma", "required": true, "data_type": "TEXT", "constraints": [], "foreign_key": {"references": "dm_trang_thai_ho_so.ma"}, "distinct_values": []}, {"name": "kho_ma", "required": true, "data_type": "TEXT", "constraints": [], "foreign_key": {"references": "dm_kho.ma"}, "distinct_values": []}, {"name": "tu_ma", "required": true, "data_type": "TEXT", "constraints": [], "foreign_key": {"references": "dm_tu.ma"}, "distinct_values": []}, {"name": "ngan_ma", "required": true, "data_type": "TEXT", "constraints": [], "foreign_key": {"references": "dm_ngan.ma"}, "distinct_values": []}, {"name": "vi_tri", "note": "VD: Kệ 2 - Hàng 5", "required": false, "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "ky_hieu", "required": false, "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "ghi_chu", "required": false, "data_type": "TEXT", "constraints": [], "distinct_values": []}], "description": "Hồ sơ bệnh án đã được lưu trữ vật lý (Sheet 3 - Thông tin hồ sơ lưu trữ)"}, {"name": "thong_tin_benh_nhan", "columns": [{"name": "so_ho_so", "required": true, "data_type": "INTEGER", "constraints": [], "primary_key": true, "distinct_values": []}, {"name": "so_benh_an", "required": true, "data_type": "TEXT", "constraints": [], "foreign_key": {"references": "ho_so_luu_tru.so_benh_an"}, "distinct_values": []}, {"pii": true, "name": "ho_ten", "required": true, "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "tuoi", "note": "0-130", "required": true, "data_type": "INTEGER", "constraints": [], "distinct_values": []}, {"name": "gioi_tinh_ma", "required": true, "data_type": "TEXT", "constraints": [], "foreign_key": {"references": "dm_gioi_tinh.ma"}, "distinct_values": []}, {"pii": true, "name": "dia_chi", "required": false, "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "nghe_nghiep", "required": false, "data_type": "TEXT", "constraints": [], "foreign_key": {"nullable": true, "references": "dm_nghe_nghiep.ma"}, "distinct_values": []}, {"name": "doi_tuong_ma", "required": true, "data_type": "TEXT", "constraints": [], "foreign_key": {"references": "dm_doi_tuong.ma"}, "distinct_values": []}, {"name": "loai_benh_an_ma", "required": true, "data_type": "TEXT", "constraints": [], "foreign_key": {"references": "dm_loai_benh_an.ma"}, "distinct_values": []}], "description": "Thông tin hành chính bệnh nhân gắn với bệnh án (Sheet 2)"}, {"name": "danh_sach_benh_nhan", "columns": [{"name": "so_ho_so", "required": true, "data_type": "INTEGER", "constraints": [], "primary_key": true, "distinct_values": []}, {"name": "so_luu_tru", "required": true, "data_type": "INTEGER", "constraints": [], "distinct_values": []}, {"pii": true, "name": "ten_benh_nhan", "required": true, "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "tuoi", "required": true, "data_type": "INTEGER", "constraints": [], "distinct_values": []}, {"name": "gioi_tinh_ma", "required": true, "data_type": "TEXT", "constraints": [], "foreign_key": {"references": "dm_gioi_tinh.ma"}, "distinct_values": []}, {"pii": true, "name": "dia_chi", "required": false, "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "thoi_gian_vao_vien", "required": true, "data_type": "DATE", "constraints": [], "distinct_values": []}, {"name": "ngay_ra", "required": false, "data_type": "DATE", "constraints": [], "distinct_values": []}, {"name": "khoa_vao_ma", "required": true, "data_type": "TEXT", "constraints": [], "foreign_key": {"references": "dm_khoa.ma_khoa"}, "distinct_values": []}, {"name": "khoa_ra_ma", "required": true, "data_type": "TEXT", "constraints": [], "foreign_key": {"references": "dm_khoa.ma_khoa"}, "distinct_values": []}, {"name": "chan_doan", "required": false, "data_type": "TEXT", "constraints": [], "distinct_values": []}], "description": "Danh sách tổng hợp toàn bộ bệnh nhân đã lưu trữ hồ sơ (Sheet 4 - dùng cho grid tổng hợp/báo cáo)"}, {"name": "dm_gioi_tinh", "columns": [{"name": "ma", "data_type": "TEXT", "constraints": [], "primary_key": true, "distinct_values": []}, {"name": "ten_hien_thi", "data_type": "TEXT", "constraints": [], "distinct_values": []}], "description": "Danh mục giới tính"}, {"name": "dm_khoa", "columns": [{"name": "ma_khoa", "data_type": "TEXT", "constraints": [], "primary_key": true, "distinct_values": []}, {"name": "ten_khoa", "data_type": "TEXT", "constraints": [], "distinct_values": []}], "description": "Danh mục khoa/phòng bệnh viện"}, {"name": "dm_doi_tuong", "columns": [{"name": "ma", "data_type": "TEXT", "constraints": [], "primary_key": true, "distinct_values": []}, {"name": "ten_hien_thi", "data_type": "TEXT", "constraints": [], "distinct_values": []}], "description": "Danh mục đối tượng chi trả viện phí"}, {"name": "dm_loai_benh_an", "columns": [{"name": "ma", "data_type": "TEXT", "constraints": [], "primary_key": true, "distinct_values": []}, {"name": "ten_hien_thi", "data_type": "TEXT", "constraints": [], "distinct_values": []}], "description": "Danh mục loại bệnh án"}, {"name": "dm_trang_thai_ho_so", "columns": [{"name": "ma", "data_type": "TEXT", "constraints": [], "primary_key": true, "distinct_values": []}, {"name": "ten_hien_thi", "data_type": "TEXT", "constraints": [], "distinct_values": []}], "description": "Danh mục trạng thái hồ sơ lưu trữ"}, {"name": "dm_kho", "columns": [{"name": "ma", "data_type": "TEXT", "constraints": [], "primary_key": true, "distinct_values": []}, {"name": "ten_hien_thi", "data_type": "TEXT", "constraints": [], "distinct_values": []}], "description": "Danh mục kho lưu trữ"}, {"name": "dm_tu", "columns": [{"name": "ma", "data_type": "TEXT", "constraints": [], "primary_key": true, "distinct_values": []}, {"name": "kho_ma", "data_type": "TEXT", "constraints": [], "foreign_key": {"references": "dm_kho.ma"}, "distinct_values": []}, {"name": "ten_hien_thi", "data_type": "TEXT", "constraints": [], "distinct_values": []}], "description": "Danh mục tủ lưu trữ (thuộc 1 kho)"}, {"name": "dm_ngan", "columns": [{"name": "ma", "data_type": "TEXT", "constraints": [], "primary_key": true, "distinct_values": []}, {"name": "tu_ma", "data_type": "TEXT", "constraints": [], "foreign_key": {"references": "dm_tu.ma"}, "distinct_values": []}, {"name": "ten_hien_thi", "data_type": "TEXT", "constraints": [], "distinct_values": []}], "description": "Danh mục ngăn lưu trữ (thuộc 1 tủ)"}, {"name": "dm_nghe_nghiep", "columns": [{"name": "ma", "data_type": "TEXT", "constraints": [], "primary_key": true, "distinct_values": []}, {"name": "ten_hien_thi", "data_type": "TEXT", "constraints": [], "distinct_values": []}], "description": "Danh mục nghề nghiệp (tùy chọn, có thể tự do dạng text)"}], "pii_fields": ["thong_tin_benh_nhan.ho_ten", "thong_tin_benh_nhan.dia_chi", "danh_sach_benh_nhan.ten_benh_nhan", "danh_sach_benh_nhan.dia_chi"], "extracted_at": "2025-11-04T09:12:00+07:00", "relationships": [{"to": "danh_sach_benh_nhan.so_ho_so", "from": "ho_so_luu_tru.so_ho_so", "type": "many_to_one"}, {"to": "ho_so_luu_tru.so_benh_an", "from": "thong_tin_benh_nhan.so_benh_an", "type": "one_to_one"}, {"to": "dm_khoa.ma_khoa", "from": "ho_so_luu_tru.khoa_vao_ma", "type": "many_to_one"}, {"to": "dm_khoa.ma_khoa", "from": "ho_so_luu_tru.khoa_ra_ma", "type": "many_to_one"}, {"to": "dm_kho.ma", "from": "ho_so_luu_tru.kho_ma", "type": "many_to_one"}, {"to": "dm_tu.ma", "from": "ho_so_luu_tru.tu_ma", "type": "many_to_one"}, {"to": "dm_ngan.ma", "from": "ho_so_luu_tru.ngan_ma", "type": "many_to_one"}, {"to": "dm_kho.ma", "from": "dm_tu.kho_ma", "type": "many_to_one"}, {"to": "dm_tu.ma", "from": "dm_ngan.tu_ma", "type": "many_to_one"}, {"to": "dm_doi_tuong.ma", "from": "thong_tin_benh_nhan.doi_tuong_ma", "type": "many_to_one"}, {"to": "dm_loai_benh_an.ma", "from": "thong_tin_benh_nhan.loai_benh_an_ma", "type": "many_to_one"}, {"to": "dm_trang_thai_ho_so.ma", "from": "ho_so_luu_tru.trang_thai_ho_so_ma", "type": "many_to_one"}], "source_system": "VIMES Patient Record - Module Hồ sơ lưu trữ", "row_count_estimate": 128450}', 'ac89f7ff-da2d-5a3d-9c94-a41fe886a788'::uuid, '2025-12-10 03:15:00+00:00', '2025-12-10 03:15:00+00:00'),
  ('2da8c727-32f8-4ce2-9528-ae87ee60077d'::uuid, 'DanhSachHoSoLuuTru.csv', 'CSV', NULL, 'D:/VinAI/P-102/backend/data/uploads/2da8c727-32f8-4ce2-9528-ae87ee60077d/DanhSachHoSoLuuTru.csv', '{"tables": [{"name": "DanhSachHoSoLuuTru", "columns": [{"name": "Số hồ sơ", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": true, "is_unique_candidate": true}, {"name": "Tên bệnh nhân", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Tuổi", "nullable": false, "data_type": "INTEGER", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 11, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Giới", "nullable": false, "data_type": "CATEGORY", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 2, "distinct_values": ["Nam", "Nữ"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Thời gian vào viện", "nullable": false, "data_type": "DATETIME", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Ngày ra", "nullable": false, "data_type": "DATETIME", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Vào từ khoa", "nullable": false, "data_type": "CATEGORY", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 8, "distinct_values": ["Khoa A7 (Nội thận - Tiết niệu)", "Khoa B9 (Tai - Mũi - Họng)", "Khoa A2 (Chấn thương chỉnh hình)", "Khoa A16 (Quốc tế)", "Khoa Khám bệnh", "Khoa Xạ trị", "Khoa B1-A (CT-Can thiệp)", "Khoa A1 (Nội tổng hợp)"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Ra từ khoa", "nullable": false, "data_type": "CATEGORY", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 8, "distinct_values": ["Khoa A7 (Nội thận - Tiết niệu)", "Khoa B9 (Tai - Mũi - Họng)", "Khoa A2 (Chấn thương chỉnh hình)", "Khoa Khám bệnh", "Khoa A16 (Quốc tế)", "Khoa B6 (Ngoại chấn thương)", "Khoa Xạ trị", "Khoa B1-A (CT-Can thiệp)"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Chẩn đoán", "nullable": false, "data_type": "CATEGORY", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 6, "distinct_values": ["Nhồi máu cơ tim cấp", "Thoát vị đĩa đệm cột sống thắt lưng", "Sỏi thận", "Đái tháo đường type 2", "Viêm xoang mạn tính", "U xơ tử cung"], "is_key_candidate": false, "is_unique_candidate": false}]}], "relationships": []}', '48116045-42fb-4bb5-8bdb-18e8f19294f7'::uuid, '2026-08-23 12:17:44.471937+00:00', '2026-08-23 12:22:38.333359+00:00'),
  ('2da8c727-32f8-4ce2-9528-ae87ee60077d'::uuid, 'ThongTinBenhNhan.csv', 'CSV', NULL, 'D:/VinAI/P-102/backend/data/uploads/2da8c727-32f8-4ce2-9528-ae87ee60077d/ThongTinBenhNhan.csv', '{"tables": [{"name": "ThongTinBenhNhan", "columns": [{"name": "Số hồ sơ", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": true, "is_unique_candidate": true}, {"name": "Số bệnh án", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Họ và tên", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Tuổi", "nullable": false, "data_type": "INTEGER", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 11, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Giới tính", "nullable": false, "data_type": "CATEGORY", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 2, "distinct_values": ["Nam", "Nữ"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Địa chỉ", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Nghề nghiệp", "nullable": false, "data_type": "CATEGORY", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 6, "distinct_values": ["Cán bộ - công chức - viên chức", "Bộ đội", "Nông dân", "Hưu trí", "Khác", "Học sinh - Sinh viên"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Đối tượng", "nullable": false, "data_type": "CATEGORY", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 4, "distinct_values": ["BHYT", "Miễn phí", "BHYT Quân", "Dịch vụ"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Loại", "nullable": false, "data_type": "CATEGORY", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 2, "distinct_values": ["Bệnh án điều trị nội trú", "Bệnh án điều trị ngoại trú"], "is_key_candidate": false, "is_unique_candidate": false}]}], "relationships": []}', '12713027-3c75-424b-b1d9-00c7321ee107'::uuid, '2026-08-23 12:17:44.481547+00:00', '2026-08-23 12:22:38.339337+00:00'),
  ('2da8c727-32f8-4ce2-9528-ae87ee60077d'::uuid, 'ThongtinHoSoLuuTru.csv', 'CSV', NULL, 'D:/VinAI/P-102/backend/data/uploads/2da8c727-32f8-4ce2-9528-ae87ee60077d/ThongtinHoSoLuuTru.csv', '{"tables": [{"name": "ThongtinHoSoLuuTru", "columns": [{"name": "Số bệnh án", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Thời gian vào viện", "nullable": false, "data_type": "DATETIME", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Ngày ra viện", "nullable": false, "data_type": "DATETIME", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Vào từ khoa", "nullable": false, "data_type": "CATEGORY", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 8, "distinct_values": ["Khoa A7 (Nội thận - Tiết niệu)", "Khoa B9 (Tai - Mũi - Họng)", "Khoa A2 (Chấn thương chỉnh hình)", "Khoa A16 (Quốc tế)", "Khoa Khám bệnh", "Khoa Xạ trị", "Khoa B1-A (CT-Can thiệp)", "Khoa A1 (Nội tổng hợp)"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Ra từ khoa", "nullable": false, "data_type": "CATEGORY", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 8, "distinct_values": ["Khoa A7 (Nội thận - Tiết niệu)", "Khoa B9 (Tai - Mũi - Họng)", "Khoa A2 (Chấn thương chỉnh hình)", "Khoa Khám bệnh", "Khoa A16 (Quốc tế)", "Khoa B6 (Ngoại chấn thương)", "Khoa Xạ trị", "Khoa B1-A (CT-Can thiệp)"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Chẩn đoán", "nullable": false, "data_type": "CATEGORY", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 6, "distinct_values": ["Nhồi máu cơ tim cấp", "Thoát vị đĩa đệm cột sống thắt lưng", "Sỏi thận", "Đái tháo đường type 2", "Viêm xoang mạn tính", "U xơ tử cung"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Số lưu trữ", "nullable": false, "data_type": "INTEGER", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Ngày lưu trữ", "nullable": false, "data_type": "DATETIME", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 11, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Trạng thái hồ sơ", "nullable": false, "data_type": "CATEGORY", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 2, "distinct_values": ["Hồ sơ chờ đưa vào kho", "Hồ sơ đang lưu trữ"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Kho", "nullable": false, "data_type": "CATEGORY", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 3, "distinct_values": ["Kho 2", "Kho 1", "Kho 3"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Tủ", "nullable": false, "data_type": "CATEGORY", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 3, "distinct_values": ["Tủ A", "Tủ B", "Tủ C"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Ngăn", "nullable": false, "data_type": "CATEGORY", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 5, "distinct_values": ["Ngăn 1", "Ngăn 4", "Ngăn 2", "Ngăn 5", "Ngăn 3"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Vị trí", "nullable": false, "data_type": "CATEGORY", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 9, "distinct_values": ["Kệ 1 - Hàng 4", "Kệ 3 - Hàng 5", "Kệ 3 - Hàng 6", "Kệ 3 - Hàng 2", "Kệ 4 - Hàng 7", "Kệ 4 - Hàng 5", "Kệ 2 - Hàng 2", "Kệ 2 - Hàng 1", "Kệ 4 - Hàng 4"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Ký hiệu", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Ghi chú", "nullable": true, "data_type": "TEXT", "null_count": 7, "constraints": [], "description": null, "primary_key": false, "distinct_count": 1, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": false}]}], "relationships": []}', '7c2636f7-68f1-4d74-9698-fd6020b3203b'::uuid, '2026-08-23 12:17:44.491020+00:00', '2026-08-23 12:22:38.346548+00:00'),
  ('c6e50b32-d59d-41d5-b634-618d8a4286c8'::uuid, 'DanhSachBenhNhan.csv', 'CSV', NULL, 'D:/VinAI/P-102/backend/data/uploads/c6e50b32-d59d-41d5-b634-618d8a4286c8/DanhSachBenhNhan.csv', 'null', 'cbadc4e4-8c2e-4845-8237-ed8d792282c5'::uuid, '2026-08-24 08:58:17.847809+00:00', '2026-08-24 08:58:17.847883+00:00'),
  ('c6e50b32-d59d-41d5-b634-618d8a4286c8'::uuid, 'DanhSachHoSoLuuTru.csv', 'CSV', NULL, 'D:/VinAI/P-102/backend/data/uploads/c6e50b32-d59d-41d5-b634-618d8a4286c8/DanhSachHoSoLuuTru.csv', 'null', '62196173-9646-4e6c-88c3-1e18bcba81b8'::uuid, '2026-08-24 08:58:17.877769+00:00', '2026-08-24 08:58:17.877833+00:00'),
  ('c6e50b32-d59d-41d5-b634-618d8a4286c8'::uuid, 'ThongTinBenhNhan.csv', 'CSV', NULL, 'D:/VinAI/P-102/backend/data/uploads/c6e50b32-d59d-41d5-b634-618d8a4286c8/ThongTinBenhNhan.csv', 'null', '475f4d48-e0a2-4a8f-8541-822cadcf9232'::uuid, '2026-08-24 08:58:17.889027+00:00', '2026-08-24 08:58:17.889083+00:00'),
  ('c6e50b32-d59d-41d5-b634-618d8a4286c8'::uuid, 'ThongtinHoSoLuuTru.csv', 'CSV', NULL, 'D:/VinAI/P-102/backend/data/uploads/c6e50b32-d59d-41d5-b634-618d8a4286c8/ThongtinHoSoLuuTru.csv', 'null', '25bd61e6-746d-437d-99f7-c54253b02ba3'::uuid, '2026-08-24 08:58:17.900252+00:00', '2026-08-24 08:58:17.900303+00:00'),
  ('6268eced-f86b-5e52-b0a9-262a806879e9'::uuid, 'Ad Platforms - Chi phí quảng cáo', 'TEXT', 'Báo cáo chi phí quảng cáo tổng hợp hàng tuần từ Facebook Ads, Google Ads, xuất dạng file TXT phân tách bởi tab.', '/uploads/ecom/weekly_ad_spend_report.txt', '{"tables": [{"name": "weekly_ad_spend_report.txt", "columns": [{"name": "campaign_id", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "channel", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "spend", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "conversions", "data_type": "INTEGER", "constraints": [], "distinct_values": []}]}], "delimiter": "\\t", "row_count_estimate": 5200}', '42c154dd-20cb-554a-9822-c76543a5e552'::uuid, '2026-01-06 03:00:00+00:00', '2026-01-06 03:00:00+00:00'),
  ('0772523a-7235-410b-8eea-ee711baa62e0'::uuid, 'ThongTinBenhNhan.csv', 'CSV', NULL, 'D:/VinAI/P-102/backend/data/uploads/0772523a-7235-410b-8eea-ee711baa62e0/ThongTinBenhNhan.csv', '{"tables": [{"name": "ThongTinBenhNhan", "columns": [{"name": "Số hồ sơ", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": true, "is_unique_candidate": true}, {"name": "Số bệnh án", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Họ và tên", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Tuổi", "nullable": false, "data_type": "INTEGER", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 11, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Giới tính", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 2, "distinct_values": ["Nam", "Nữ"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Địa chỉ", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Nghề nghiệp", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 6, "distinct_values": ["Cán bộ - công chức - viên chức", "Bộ đội", "Nông dân", "Hưu trí", "Khác", "Học sinh - Sinh viên"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Đối tượng", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 4, "distinct_values": ["BHYT", "Miễn phí", "BHYT Quân", "Dịch vụ"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Loại", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 2, "distinct_values": ["Bệnh án điều trị nội trú", "Bệnh án điều trị ngoại trú"], "is_key_candidate": false, "is_unique_candidate": false}]}], "relationships": []}', '2dd89a73-f30b-4a5d-95f9-4a994095ea2b'::uuid, '2026-08-22 09:52:59.306752+00:00', '2026-08-22 11:09:05.788402+00:00'),
  ('b2f95613-a6f8-5e35-b6d7-e03bf1cc7aae'::uuid, 'CRM - Hồ sơ khách hàng', 'JSON', 'Export định kỳ dạng JSON từ hệ thống CRM chứa thông tin phân khúc khách hàng và điểm tín dụng nội bộ.', 's3://bank-data-lake/crm/customer_profile/', '{"tables": [{"name": "customer_profile.json", "columns": [{"name": "customer_id", "data_type": "INTEGER", "constraints": [], "distinct_values": []}, {"name": "segment", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "risk_score", "data_type": "INTEGER", "constraints": [], "distinct_values": []}, {"name": "kyc_status", "data_type": "TEXT", "constraints": [], "distinct_values": []}]}], "row_count_estimate": 980000}', 'aa87a790-835d-5d2e-82f2-a6758588dda5'::uuid, '2025-11-09 02:00:00+00:00', '2025-11-09 02:00:00+00:00'),
  ('0baed64b-d380-4a01-a64b-265af7059568'::uuid, 'DanhSachBenhNhan.csv', 'CSV', NULL, 'D:/VinAI/P-102/backend/data/uploads/0baed64b-d380-4a01-a64b-265af7059568/DanhSachBenhNhan.csv', '{"tables": [{"name": "danh_sach_benh_nhan", "columns": [{"name": "so_ho_so", "nullable": false, "data_type": "TEXT", "constraints": [{"type": "UNIQUE"}], "description": "Số hồ sơ của bệnh nhân", "primary_key": true, "distinct_values": []}, {"name": "so_luu_tru", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Số lưu trữ hồ sơ bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "ten_benh_nhan", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Tên đầy đủ của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "tuoi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Tuổi của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "gioi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Giới tính của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "dia_chi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Địa chỉ thường trú của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "thoi_gian_vao_vien", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Thời gian bệnh nhân vào viện", "primary_key": false, "distinct_values": []}, {"name": "ngay_ra", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Ngày bệnh nhân ra viện", "primary_key": false, "distinct_values": []}, {"name": "vao_tu_khoa", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Khoa điều trị tiếp nhận ban đầu", "primary_key": false, "distinct_values": []}, {"name": "ra_tu_khoa", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Khoa điều trị cho ra viện", "primary_key": false, "distinct_values": []}, {"name": "chan_doan", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Chẩn đoán bệnh lý chính", "primary_key": false, "distinct_values": []}]}, {"name": "danh_sach_ho_so_luu_tru", "columns": [{"name": "so_ho_so", "nullable": false, "data_type": "TEXT", "constraints": [{"type": "UNIQUE"}, {"type": "FOREIGN_KEY", "reference_table": "danh_sach_benh_nhan", "reference_column": "so_ho_so"}], "description": "Số hồ sơ liên kết", "primary_key": true, "distinct_values": []}, {"name": "ten_benh_nhan", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Tên bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "tuoi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Tuổi bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "gioi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Giới tính", "primary_key": false, "distinct_values": []}, {"name": "thoi_gian_vao_vien", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Thời gian vào viện", "primary_key": false, "distinct_values": []}, {"name": "ngay_ra", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Ngày ra viện", "primary_key": false, "distinct_values": []}, {"name": "vao_tu_khoa", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Khoa tiếp nhận bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "ra_tu_khoa", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Khoa cho xuất viện", "primary_key": false, "distinct_values": []}, {"name": "chan_doan", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Chẩn đoán lâm sàng", "primary_key": false, "distinct_values": []}]}, {"name": "thong_tin_benh_nhan", "columns": [{"name": "so_ho_so", "nullable": false, "data_type": "TEXT", "constraints": [{"type": "UNIQUE"}, {"type": "FOREIGN_KEY", "reference_table": "danh_sach_benh_nhan", "reference_column": "so_ho_so"}], "description": "Số hồ sơ bệnh nhân", "primary_key": true, "distinct_values": []}, {"name": "so_benh_an", "nullable": false, "data_type": "TEXT", "constraints": [{"type": "UNIQUE"}, {"type": "FOREIGN_KEY", "reference_table": "thong_tin_ho_so_luu_tru", "reference_column": "so_benh_an"}], "description": "Số bệnh án của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "ho_va_ten", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Họ và tên bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "tuoi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Tuổi bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "gioi_tinh", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Giới tính của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "dia_chi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Địa chỉ của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "nghe_nghiep", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Nghề nghiệp của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "doi_tuong", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Đối tượng điều trị", "primary_key": false, "distinct_values": []}, {"name": "loai", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Loại bệnh án", "primary_key": false, "distinct_values": []}]}, {"name": "thong_tin_ho_so_luu_tru", "columns": [{"name": "so_benh_an", "nullable": false, "data_type": "TEXT", "constraints": [{"type": "UNIQUE"}], "description": "Số bệnh án lưu trữ", "primary_key": true, "distinct_values": []}, {"name": "thoi_gian_vao_vien", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Thời gian bệnh nhân nhập viện", "primary_key": false, "distinct_values": []}, {"name": "ngay_ra_vien", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Ngày ra viện", "primary_key": false, "distinct_values": []}, {"name": "vao_tu_khoa", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Khoa tiếp nhận lúc vào viện", "primary_key": false, "distinct_values": []}, {"name": "ra_tu_khoa", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Khoa điều trị lúc ra viện", "primary_key": false, "distinct_values": []}, {"name": "chan_doan", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Chẩn đoán bệnh án", "primary_key": false, "distinct_values": []}, {"name": "so_luu_tru", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Số lưu trữ của hồ sơ bệnh án", "primary_key": false, "distinct_values": []}, {"name": "ngay_luu_tru", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Ngày lưu trữ hồ sơ bệnh án", "primary_key": false, "distinct_values": []}, {"name": "trang_thai_ho_so", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Trạng thái hiện tại của hồ sơ", "primary_key": false, "distinct_values": []}, {"name": "kho", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Kho lưu trữ vật lý", "primary_key": false, "distinct_values": []}, {"name": "tu", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Tủ lưu trữ vật lý", "primary_key": false, "distinct_values": []}, {"name": "ngan", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Ngăn lưu trữ vật lý", "primary_key": false, "distinct_values": []}, {"name": "vi_tri", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Vị trí lưu trữ chi tiết", "primary_key": false, "distinct_values": []}, {"name": "ky_hieu", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Ký hiệu hồ sơ lưu trữ", "primary_key": false, "distinct_values": []}, {"name": "ghi_chu", "nullable": true, "data_type": "TEXT", "constraints": [], "description": "Ghi chú thêm về hồ sơ lưu trữ", "primary_key": false, "distinct_values": []}]}], "relationships": [{"type": "one_to_one", "to_column": "danh_sach_benh_nhan.so_ho_so", "from_column": "danh_sach_ho_so_luu_tru.so_ho_so"}, {"type": "one_to_one", "to_column": "danh_sach_benh_nhan.so_ho_so", "from_column": "thong_tin_benh_nhan.so_ho_so"}, {"type": "one_to_one", "to_column": "thong_tin_ho_so_luu_tru.so_benh_an", "from_column": "thong_tin_benh_nhan.so_benh_an"}]}', '308651ce-5743-4c08-817d-ec3654af7597'::uuid, '2026-08-17 09:10:56.181438+00:00', '2026-08-17 10:02:55.481706+00:00'),
  ('0baed64b-d380-4a01-a64b-265af7059568'::uuid, 'DanhSachHoSoLuuTru.csv', 'CSV', NULL, 'D:/VinAI/P-102/backend/data/uploads/0baed64b-d380-4a01-a64b-265af7059568/DanhSachHoSoLuuTru.csv', '{"tables": [{"name": "danh_sach_benh_nhan", "columns": [{"name": "so_ho_so", "nullable": false, "data_type": "TEXT", "constraints": [{"type": "UNIQUE"}], "description": "Số hồ sơ của bệnh nhân", "primary_key": true, "distinct_values": []}, {"name": "so_luu_tru", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Số lưu trữ hồ sơ bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "ten_benh_nhan", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Tên đầy đủ của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "tuoi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Tuổi của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "gioi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Giới tính của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "dia_chi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Địa chỉ thường trú của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "thoi_gian_vao_vien", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Thời gian bệnh nhân vào viện", "primary_key": false, "distinct_values": []}, {"name": "ngay_ra", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Ngày bệnh nhân ra viện", "primary_key": false, "distinct_values": []}, {"name": "vao_tu_khoa", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Khoa điều trị tiếp nhận ban đầu", "primary_key": false, "distinct_values": []}, {"name": "ra_tu_khoa", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Khoa điều trị cho ra viện", "primary_key": false, "distinct_values": []}, {"name": "chan_doan", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Chẩn đoán bệnh lý chính", "primary_key": false, "distinct_values": []}]}, {"name": "danh_sach_ho_so_luu_tru", "columns": [{"name": "so_ho_so", "nullable": false, "data_type": "TEXT", "constraints": [{"type": "UNIQUE"}, {"type": "FOREIGN_KEY", "reference_table": "danh_sach_benh_nhan", "reference_column": "so_ho_so"}], "description": "Số hồ sơ liên kết", "primary_key": true, "distinct_values": []}, {"name": "ten_benh_nhan", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Tên bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "tuoi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Tuổi bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "gioi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Giới tính", "primary_key": false, "distinct_values": []}, {"name": "thoi_gian_vao_vien", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Thời gian vào viện", "primary_key": false, "distinct_values": []}, {"name": "ngay_ra", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Ngày ra viện", "primary_key": false, "distinct_values": []}, {"name": "vao_tu_khoa", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Khoa tiếp nhận bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "ra_tu_khoa", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Khoa cho xuất viện", "primary_key": false, "distinct_values": []}, {"name": "chan_doan", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Chẩn đoán lâm sàng", "primary_key": false, "distinct_values": []}]}, {"name": "thong_tin_benh_nhan", "columns": [{"name": "so_ho_so", "nullable": false, "data_type": "TEXT", "constraints": [{"type": "UNIQUE"}, {"type": "FOREIGN_KEY", "reference_table": "danh_sach_benh_nhan", "reference_column": "so_ho_so"}], "description": "Số hồ sơ bệnh nhân", "primary_key": true, "distinct_values": []}, {"name": "so_benh_an", "nullable": false, "data_type": "TEXT", "constraints": [{"type": "UNIQUE"}, {"type": "FOREIGN_KEY", "reference_table": "thong_tin_ho_so_luu_tru", "reference_column": "so_benh_an"}], "description": "Số bệnh án của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "ho_va_ten", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Họ và tên bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "tuoi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Tuổi bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "gioi_tinh", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Giới tính của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "dia_chi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Địa chỉ của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "nghe_nghiep", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Nghề nghiệp của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "doi_tuong", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Đối tượng điều trị", "primary_key": false, "distinct_values": []}, {"name": "loai", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Loại bệnh án", "primary_key": false, "distinct_values": []}]}, {"name": "thong_tin_ho_so_luu_tru", "columns": [{"name": "so_benh_an", "nullable": false, "data_type": "TEXT", "constraints": [{"type": "UNIQUE"}], "description": "Số bệnh án lưu trữ", "primary_key": true, "distinct_values": []}, {"name": "thoi_gian_vao_vien", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Thời gian bệnh nhân nhập viện", "primary_key": false, "distinct_values": []}, {"name": "ngay_ra_vien", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Ngày ra viện", "primary_key": false, "distinct_values": []}, {"name": "vao_tu_khoa", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Khoa tiếp nhận lúc vào viện", "primary_key": false, "distinct_values": []}, {"name": "ra_tu_khoa", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Khoa điều trị lúc ra viện", "primary_key": false, "distinct_values": []}, {"name": "chan_doan", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Chẩn đoán bệnh án", "primary_key": false, "distinct_values": []}, {"name": "so_luu_tru", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Số lưu trữ của hồ sơ bệnh án", "primary_key": false, "distinct_values": []}, {"name": "ngay_luu_tru", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Ngày lưu trữ hồ sơ bệnh án", "primary_key": false, "distinct_values": []}, {"name": "trang_thai_ho_so", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Trạng thái hiện tại của hồ sơ", "primary_key": false, "distinct_values": []}, {"name": "kho", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Kho lưu trữ vật lý", "primary_key": false, "distinct_values": []}, {"name": "tu", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Tủ lưu trữ vật lý", "primary_key": false, "distinct_values": []}, {"name": "ngan", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Ngăn lưu trữ vật lý", "primary_key": false, "distinct_values": []}, {"name": "vi_tri", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Vị trí lưu trữ chi tiết", "primary_key": false, "distinct_values": []}, {"name": "ky_hieu", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Ký hiệu hồ sơ lưu trữ", "primary_key": false, "distinct_values": []}, {"name": "ghi_chu", "nullable": true, "data_type": "TEXT", "constraints": [], "description": "Ghi chú thêm về hồ sơ lưu trữ", "primary_key": false, "distinct_values": []}]}], "relationships": [{"type": "one_to_one", "to_column": "danh_sach_benh_nhan.so_ho_so", "from_column": "danh_sach_ho_so_luu_tru.so_ho_so"}, {"type": "one_to_one", "to_column": "danh_sach_benh_nhan.so_ho_so", "from_column": "thong_tin_benh_nhan.so_ho_so"}, {"type": "one_to_one", "to_column": "thong_tin_ho_so_luu_tru.so_benh_an", "from_column": "thong_tin_benh_nhan.so_benh_an"}]}', '0b5936c4-ffd4-4937-968a-41d3da19fe0a'::uuid, '2026-08-17 09:10:56.222450+00:00', '2026-08-17 10:02:55.508729+00:00'),
  ('0baed64b-d380-4a01-a64b-265af7059568'::uuid, 'ThongTinBenhNhan.csv', 'CSV', NULL, 'D:/VinAI/P-102/backend/data/uploads/0baed64b-d380-4a01-a64b-265af7059568/ThongTinBenhNhan.csv', '{"tables": [{"name": "danh_sach_benh_nhan", "columns": [{"name": "so_ho_so", "nullable": false, "data_type": "TEXT", "constraints": [{"type": "UNIQUE"}], "description": "Số hồ sơ của bệnh nhân", "primary_key": true, "distinct_values": []}, {"name": "so_luu_tru", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Số lưu trữ hồ sơ bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "ten_benh_nhan", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Tên đầy đủ của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "tuoi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Tuổi của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "gioi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Giới tính của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "dia_chi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Địa chỉ thường trú của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "thoi_gian_vao_vien", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Thời gian bệnh nhân vào viện", "primary_key": false, "distinct_values": []}, {"name": "ngay_ra", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Ngày bệnh nhân ra viện", "primary_key": false, "distinct_values": []}, {"name": "vao_tu_khoa", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Khoa điều trị tiếp nhận ban đầu", "primary_key": false, "distinct_values": []}, {"name": "ra_tu_khoa", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Khoa điều trị cho ra viện", "primary_key": false, "distinct_values": []}, {"name": "chan_doan", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Chẩn đoán bệnh lý chính", "primary_key": false, "distinct_values": []}]}, {"name": "danh_sach_ho_so_luu_tru", "columns": [{"name": "so_ho_so", "nullable": false, "data_type": "TEXT", "constraints": [{"type": "UNIQUE"}, {"type": "FOREIGN_KEY", "reference_table": "danh_sach_benh_nhan", "reference_column": "so_ho_so"}], "description": "Số hồ sơ liên kết", "primary_key": true, "distinct_values": []}, {"name": "ten_benh_nhan", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Tên bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "tuoi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Tuổi bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "gioi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Giới tính", "primary_key": false, "distinct_values": []}, {"name": "thoi_gian_vao_vien", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Thời gian vào viện", "primary_key": false, "distinct_values": []}, {"name": "ngay_ra", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Ngày ra viện", "primary_key": false, "distinct_values": []}, {"name": "vao_tu_khoa", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Khoa tiếp nhận bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "ra_tu_khoa", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Khoa cho xuất viện", "primary_key": false, "distinct_values": []}, {"name": "chan_doan", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Chẩn đoán lâm sàng", "primary_key": false, "distinct_values": []}]}, {"name": "thong_tin_benh_nhan", "columns": [{"name": "so_ho_so", "nullable": false, "data_type": "TEXT", "constraints": [{"type": "UNIQUE"}, {"type": "FOREIGN_KEY", "reference_table": "danh_sach_benh_nhan", "reference_column": "so_ho_so"}], "description": "Số hồ sơ bệnh nhân", "primary_key": true, "distinct_values": []}, {"name": "so_benh_an", "nullable": false, "data_type": "TEXT", "constraints": [{"type": "UNIQUE"}, {"type": "FOREIGN_KEY", "reference_table": "thong_tin_ho_so_luu_tru", "reference_column": "so_benh_an"}], "description": "Số bệnh án của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "ho_va_ten", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Họ và tên bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "tuoi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Tuổi bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "gioi_tinh", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Giới tính của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "dia_chi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Địa chỉ của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "nghe_nghiep", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Nghề nghiệp của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "doi_tuong", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Đối tượng điều trị", "primary_key": false, "distinct_values": []}, {"name": "loai", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Loại bệnh án", "primary_key": false, "distinct_values": []}]}, {"name": "thong_tin_ho_so_luu_tru", "columns": [{"name": "so_benh_an", "nullable": false, "data_type": "TEXT", "constraints": [{"type": "UNIQUE"}], "description": "Số bệnh án lưu trữ", "primary_key": true, "distinct_values": []}, {"name": "thoi_gian_vao_vien", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Thời gian bệnh nhân nhập viện", "primary_key": false, "distinct_values": []}, {"name": "ngay_ra_vien", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Ngày ra viện", "primary_key": false, "distinct_values": []}, {"name": "vao_tu_khoa", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Khoa tiếp nhận lúc vào viện", "primary_key": false, "distinct_values": []}, {"name": "ra_tu_khoa", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Khoa điều trị lúc ra viện", "primary_key": false, "distinct_values": []}, {"name": "chan_doan", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Chẩn đoán bệnh án", "primary_key": false, "distinct_values": []}, {"name": "so_luu_tru", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Số lưu trữ của hồ sơ bệnh án", "primary_key": false, "distinct_values": []}, {"name": "ngay_luu_tru", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Ngày lưu trữ hồ sơ bệnh án", "primary_key": false, "distinct_values": []}, {"name": "trang_thai_ho_so", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Trạng thái hiện tại của hồ sơ", "primary_key": false, "distinct_values": []}, {"name": "kho", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Kho lưu trữ vật lý", "primary_key": false, "distinct_values": []}, {"name": "tu", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Tủ lưu trữ vật lý", "primary_key": false, "distinct_values": []}, {"name": "ngan", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Ngăn lưu trữ vật lý", "primary_key": false, "distinct_values": []}, {"name": "vi_tri", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Vị trí lưu trữ chi tiết", "primary_key": false, "distinct_values": []}, {"name": "ky_hieu", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Ký hiệu hồ sơ lưu trữ", "primary_key": false, "distinct_values": []}, {"name": "ghi_chu", "nullable": true, "data_type": "TEXT", "constraints": [], "description": "Ghi chú thêm về hồ sơ lưu trữ", "primary_key": false, "distinct_values": []}]}], "relationships": [{"type": "one_to_one", "to_column": "danh_sach_benh_nhan.so_ho_so", "from_column": "danh_sach_ho_so_luu_tru.so_ho_so"}, {"type": "one_to_one", "to_column": "danh_sach_benh_nhan.so_ho_so", "from_column": "thong_tin_benh_nhan.so_ho_so"}, {"type": "one_to_one", "to_column": "thong_tin_ho_so_luu_tru.so_benh_an", "from_column": "thong_tin_benh_nhan.so_benh_an"}]}', 'dba402d0-3950-4f6e-b4d1-c47ad187b928'::uuid, '2026-08-17 09:10:56.237197+00:00', '2026-08-17 10:02:55.519045+00:00'),
  ('54505703-ca04-5613-9f4a-d2499f12ee3d'::uuid, 'Sàn TMĐT nội bộ - Đơn hàng online', 'JSON', 'API export đơn hàng từ nền tảng thương mại điện tử nội bộ của chuỗi siêu thị.', 'https://api.retailchain.vn/v2/orders/export', '{"tables": [{"name": "online_orders", "columns": [{"name": "order_id", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "sku", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "qty", "data_type": "INTEGER", "constraints": [], "distinct_values": []}, {"name": "total_amount", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "created_at", "data_type": "TEXT", "constraints": [], "distinct_values": []}]}], "row_count_estimate": 1200000}', '1ba6a112-bf9f-52ae-b631-28fee8d3f1d6'::uuid, '2025-11-12 03:00:00+00:00', '2025-11-12 03:00:00+00:00'),
  ('f8c4432f-0252-5275-a581-958039b98639'::uuid, 'Billing - Cước & lưu lượng thuê bao', 'CSV', 'File CSV xuất hàng ngày từ hệ thống tính cước (Billing) chứa lưu lượng data/thoại và doanh thu ARPU theo thuê bao.', 'sftp://billing-export.telco.vn/daily_usage/', '{"tables": [{"name": "subscribers", "columns": [{"pii": true, "name": "msisdn", "data_type": "TEXT", "constraints": [], "primary_key": true, "distinct_values": []}, {"name": "plan_code", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "region", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "activation_date", "data_type": "DATE", "constraints": [], "distinct_values": []}, {"name": "status", "data_type": "TEXT", "constraints": [], "distinct_values": []}]}, {"name": "usage_daily", "columns": [{"name": "msisdn", "data_type": "TEXT", "constraints": [], "foreign_key": {"references": "subscribers.msisdn"}, "distinct_values": []}, {"name": "usage_date", "data_type": "DATE", "constraints": [], "distinct_values": []}, {"name": "data_mb", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "voice_minutes", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "arpu", "data_type": "TEXT", "constraints": [], "distinct_values": []}]}], "relationships": [{"to": "subscribers.msisdn", "from": "usage_daily.msisdn", "type": "many_to_one"}], "row_count_estimate": 41000000}', '1951bbd1-55d5-5bdc-a11b-4150696b0c07'::uuid, '2025-12-15 02:45:00+00:00', '2025-12-15 02:45:00+00:00'),
  ('6268eced-f86b-5e52-b0a9-262a806879e9'::uuid, 'Clickstream - Hành vi người dùng', 'JSON', 'Dữ liệu clickstream (session, sự kiện giỏ hàng) thu thập qua Segment, lưu trên S3 theo định dạng JSON Lines.', 's3://ecom-data-lake/clickstream/events/', '{"tables": [{"name": "sessions", "columns": [{"name": "session_id", "data_type": "TEXT", "constraints": [], "primary_key": true, "distinct_values": []}, {"name": "user_id", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "channel", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "started_at", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "device", "data_type": "TEXT", "constraints": [], "distinct_values": []}]}, {"name": "cart_events", "columns": [{"name": "event_id", "data_type": "TEXT", "constraints": [], "primary_key": true, "distinct_values": []}, {"name": "session_id", "data_type": "TEXT", "constraints": [], "foreign_key": {"references": "sessions.session_id"}, "distinct_values": []}, {"name": "sku", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "category", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "event_type", "note": "add_to_cart, remove_from_cart, checkout, purchase", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "event_time", "data_type": "TEXT", "constraints": [], "distinct_values": []}]}, {"name": "ad_spend", "columns": [{"name": "campaign_id", "data_type": "TEXT", "constraints": [], "primary_key": true, "distinct_values": []}, {"name": "channel", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "spend", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "clicks", "data_type": "INTEGER", "constraints": [], "distinct_values": []}, {"name": "conversions", "data_type": "INTEGER", "constraints": [], "distinct_values": []}, {"name": "report_date", "data_type": "DATE", "constraints": [], "distinct_values": []}]}], "relationships": [{"to": "sessions.session_id", "from": "cart_events.session_id", "type": "many_to_one"}], "row_count_estimate": 7300000}', 'eda2a896-1250-56e5-b7bd-b8162f8af175'::uuid, '2026-01-05 03:20:00+00:00', '2026-01-05 03:20:00+00:00'),
  ('b2f95613-a6f8-5e35-b6d7-e03bf1cc7aae'::uuid, 'Core Banking - Giao dịch & Tài khoản', 'SQL', 'Kết nối trực tiếp tới Core Banking (Oracle) lấy dữ liệu khách hàng, tài khoản và giao dịch hàng ngày.', 'oracle://corebanking.internal:1521/CBSPROD', '{"tables": [{"name": "customers", "columns": [{"name": "customer_id", "data_type": "INTEGER", "constraints": [], "primary_key": true, "distinct_values": []}, {"pii": true, "name": "full_name", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"pii": true, "name": "national_id", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"pii": true, "name": "phone", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "customer_segment", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "credit_score", "data_type": "INTEGER", "constraints": [], "distinct_values": []}]}, {"name": "accounts", "columns": [{"pii": true, "name": "account_no", "data_type": "TEXT", "constraints": [], "primary_key": true, "distinct_values": []}, {"name": "customer_id", "data_type": "INTEGER", "constraints": [], "foreign_key": {"references": "customers.customer_id"}, "distinct_values": []}, {"name": "account_type", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "balance", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "open_date", "data_type": "DATE", "constraints": [], "distinct_values": []}]}, {"name": "transactions", "columns": [{"name": "transaction_id", "data_type": "INTEGER", "constraints": [], "primary_key": true, "distinct_values": []}, {"name": "account_no", "data_type": "TEXT", "constraints": [], "foreign_key": {"references": "accounts.account_no"}, "distinct_values": []}, {"name": "channel", "note": "ATM, IB, POS, MOBILE", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "amount", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "transaction_time", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "is_flagged", "data_type": "BOOLEAN", "constraints": [], "distinct_values": []}]}], "relationships": [{"to": "customers.customer_id", "from": "accounts.customer_id", "type": "many_to_one"}, {"to": "accounts.account_no", "from": "transactions.account_no", "type": "many_to_one"}], "row_count_estimate": 2400000}', '0d250b43-72b6-59c3-9a28-834d75af393f'::uuid, '2025-11-08 01:45:00+00:00', '2025-11-08 01:45:00+00:00'),
  ('54505703-ca04-5613-9f4a-d2499f12ee3d'::uuid, 'POS - Dữ liệu bán hàng tại quầy', 'CSV', 'File CSV xuất hàng ngày từ 120 cửa hàng, chứa chi tiết hóa đơn bán hàng theo SKU.', 'sftp://pos-export.retailchain.vn/daily/', '{"tables": [{"name": "pos_transactions.csv", "columns": [{"name": "invoice_no", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "store_code", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "sku", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "category", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "qty", "data_type": "INTEGER", "constraints": [], "distinct_values": []}, {"name": "unit_price", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "discount_pct", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "sold_at", "data_type": "TEXT", "constraints": [], "distinct_values": []}]}, {"name": "stores.csv", "columns": [{"name": "store_code", "data_type": "TEXT", "constraints": [], "primary_key": true, "distinct_values": []}, {"name": "region", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "store_type", "data_type": "TEXT", "constraints": [], "distinct_values": []}]}], "encoding": "UTF-8", "delimiter": ",", "relationships": [{"to": "stores.csv.store_code", "from": "pos_transactions.csv.store_code", "type": "many_to_one"}], "row_count_estimate": 5600000}', 'f46d150c-c76d-5b15-8c79-46f130fbd6fe'::uuid, '2025-11-11 02:30:00+00:00', '2025-11-11 02:30:00+00:00'),
  ('b05c0f83-d93a-439b-bb1a-f7c109af8201'::uuid, 'ThongTinBenhNhan.csv', 'CSV', NULL, 'D:/VinAI/P-102/backend/data/uploads/b05c0f83-d93a-439b-bb1a-f7c109af8201/ThongTinBenhNhan.csv', '{"tables": [{"name": "ThongTinBenhNhan", "columns": [{"name": "Số hồ sơ", "nullable": false, "data_type": "INTEGER", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": []}, {"name": "Số bệnh án", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": []}, {"name": "Họ và tên", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": []}, {"name": "Tuổi", "nullable": false, "data_type": "INTEGER", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 11, "distinct_values": []}, {"name": "Giới tính", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 2, "distinct_values": ["Nam", "Nữ"]}, {"name": "Địa chỉ", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": []}, {"name": "Nghề nghiệp", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 6, "distinct_values": []}, {"name": "Đối tượng", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 4, "distinct_values": []}, {"name": "Loại", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 2, "distinct_values": ["Bệnh án điều trị nội trú", "Bệnh án điều trị ngoại trú"]}]}], "relationships": []}', '7b986e0f-b105-4974-bc81-80bf08958c4a'::uuid, '2026-08-22 02:08:07.623437+00:00', '2026-08-22 02:08:07.623470+00:00'),
  ('b05c0f83-d93a-439b-bb1a-f7c109af8201'::uuid, 'ThongtinHoSoLuuTru.csv', 'CSV', NULL, 'D:/VinAI/P-102/backend/data/uploads/b05c0f83-d93a-439b-bb1a-f7c109af8201/ThongtinHoSoLuuTru.csv', '{"tables": [{"name": "ThongtinHoSoLuuTru", "columns": [{"name": "Số bệnh án", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": []}, {"name": "Thời gian vào viện", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": []}, {"name": "Ngày ra viện", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": []}, {"name": "Vào từ khoa", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 8, "distinct_values": []}, {"name": "Ra từ khoa", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 8, "distinct_values": []}, {"name": "Chẩn đoán", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 6, "distinct_values": []}, {"name": "Số lưu trữ", "nullable": false, "data_type": "INTEGER", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": []}, {"name": "Ngày lưu trữ", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 11, "distinct_values": []}, {"name": "Trạng thái hồ sơ", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 2, "distinct_values": ["Hồ sơ chờ đưa vào kho", "Hồ sơ đang lưu trữ"]}, {"name": "Kho", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 3, "distinct_values": []}, {"name": "Tủ", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 3, "distinct_values": []}, {"name": "Ngăn", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 5, "distinct_values": []}, {"name": "Vị trí", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 9, "distinct_values": []}, {"name": "Ký hiệu", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": []}, {"name": "Ghi chú", "nullable": true, "data_type": "TEXT", "null_count": 7, "constraints": [], "description": null, "primary_key": false, "distinct_count": 1, "distinct_values": ["Hồ sơ cần bổ sung xét nghiệm"]}]}], "relationships": []}', '849a6c10-42ad-4224-af64-5a212675c337'::uuid, '2026-08-22 02:08:07.782201+00:00', '2026-08-22 02:08:07.782235+00:00'),
  ('b05c0f83-d93a-439b-bb1a-f7c109af8201'::uuid, 'DanhSachHoSoLuuTru.csv', 'CSV', NULL, 'D:/VinAI/P-102/backend/data/uploads/b05c0f83-d93a-439b-bb1a-f7c109af8201/DanhSachHoSoLuuTru.csv', '{"tables": [{"name": "DanhSachHoSoLuuTru", "columns": [{"name": "Số hồ sơ", "nullable": false, "data_type": "INTEGER", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": []}, {"name": "Tên bệnh nhân", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": []}, {"name": "Tuổi", "nullable": false, "data_type": "INTEGER", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 11, "distinct_values": []}, {"name": "Giới", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 2, "distinct_values": ["Nam", "Nữ"]}, {"name": "Thời gian vào viện", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": []}, {"name": "Ngày ra", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": []}, {"name": "Vào từ khoa", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 8, "distinct_values": []}, {"name": "Ra từ khoa", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 8, "distinct_values": []}, {"name": "Chẩn đoán", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 6, "distinct_values": []}]}], "relationships": []}', 'b88cdb41-6400-4195-8209-2e9ff4840006'::uuid, '2026-08-22 02:08:07.490261+00:00', '2026-08-22 02:08:55.275428+00:00'),
  ('0baed64b-d380-4a01-a64b-265af7059568'::uuid, 'ThongtinHoSoLuuTru.csv', 'CSV', NULL, 'D:/VinAI/P-102/backend/data/uploads/0baed64b-d380-4a01-a64b-265af7059568/ThongtinHoSoLuuTru.csv', '{"tables": [{"name": "danh_sach_benh_nhan", "columns": [{"name": "so_ho_so", "nullable": false, "data_type": "TEXT", "constraints": [{"type": "UNIQUE"}], "description": "Số hồ sơ của bệnh nhân", "primary_key": true, "distinct_values": []}, {"name": "so_luu_tru", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Số lưu trữ hồ sơ bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "ten_benh_nhan", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Tên đầy đủ của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "tuoi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Tuổi của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "gioi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Giới tính của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "dia_chi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Địa chỉ thường trú của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "thoi_gian_vao_vien", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Thời gian bệnh nhân vào viện", "primary_key": false, "distinct_values": []}, {"name": "ngay_ra", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Ngày bệnh nhân ra viện", "primary_key": false, "distinct_values": []}, {"name": "vao_tu_khoa", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Khoa điều trị tiếp nhận ban đầu", "primary_key": false, "distinct_values": []}, {"name": "ra_tu_khoa", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Khoa điều trị cho ra viện", "primary_key": false, "distinct_values": []}, {"name": "chan_doan", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Chẩn đoán bệnh lý chính", "primary_key": false, "distinct_values": []}]}, {"name": "danh_sach_ho_so_luu_tru", "columns": [{"name": "so_ho_so", "nullable": false, "data_type": "TEXT", "constraints": [{"type": "UNIQUE"}, {"type": "FOREIGN_KEY", "reference_table": "danh_sach_benh_nhan", "reference_column": "so_ho_so"}], "description": "Số hồ sơ liên kết", "primary_key": true, "distinct_values": []}, {"name": "ten_benh_nhan", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Tên bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "tuoi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Tuổi bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "gioi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Giới tính", "primary_key": false, "distinct_values": []}, {"name": "thoi_gian_vao_vien", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Thời gian vào viện", "primary_key": false, "distinct_values": []}, {"name": "ngay_ra", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Ngày ra viện", "primary_key": false, "distinct_values": []}, {"name": "vao_tu_khoa", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Khoa tiếp nhận bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "ra_tu_khoa", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Khoa cho xuất viện", "primary_key": false, "distinct_values": []}, {"name": "chan_doan", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Chẩn đoán lâm sàng", "primary_key": false, "distinct_values": []}]}, {"name": "thong_tin_benh_nhan", "columns": [{"name": "so_ho_so", "nullable": false, "data_type": "TEXT", "constraints": [{"type": "UNIQUE"}, {"type": "FOREIGN_KEY", "reference_table": "danh_sach_benh_nhan", "reference_column": "so_ho_so"}], "description": "Số hồ sơ bệnh nhân", "primary_key": true, "distinct_values": []}, {"name": "so_benh_an", "nullable": false, "data_type": "TEXT", "constraints": [{"type": "UNIQUE"}, {"type": "FOREIGN_KEY", "reference_table": "thong_tin_ho_so_luu_tru", "reference_column": "so_benh_an"}], "description": "Số bệnh án của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "ho_va_ten", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Họ và tên bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "tuoi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Tuổi bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "gioi_tinh", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Giới tính của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "dia_chi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Địa chỉ của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "nghe_nghiep", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Nghề nghiệp của bệnh nhân", "primary_key": false, "distinct_values": []}, {"name": "doi_tuong", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Đối tượng điều trị", "primary_key": false, "distinct_values": []}, {"name": "loai", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Loại bệnh án", "primary_key": false, "distinct_values": []}]}, {"name": "thong_tin_ho_so_luu_tru", "columns": [{"name": "so_benh_an", "nullable": false, "data_type": "TEXT", "constraints": [{"type": "UNIQUE"}], "description": "Số bệnh án lưu trữ", "primary_key": true, "distinct_values": []}, {"name": "thoi_gian_vao_vien", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Thời gian bệnh nhân nhập viện", "primary_key": false, "distinct_values": []}, {"name": "ngay_ra_vien", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Ngày ra viện", "primary_key": false, "distinct_values": []}, {"name": "vao_tu_khoa", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Khoa tiếp nhận lúc vào viện", "primary_key": false, "distinct_values": []}, {"name": "ra_tu_khoa", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Khoa điều trị lúc ra viện", "primary_key": false, "distinct_values": []}, {"name": "chan_doan", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Chẩn đoán bệnh án", "primary_key": false, "distinct_values": []}, {"name": "so_luu_tru", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Số lưu trữ của hồ sơ bệnh án", "primary_key": false, "distinct_values": []}, {"name": "ngay_luu_tru", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Ngày lưu trữ hồ sơ bệnh án", "primary_key": false, "distinct_values": []}, {"name": "trang_thai_ho_so", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Trạng thái hiện tại của hồ sơ", "primary_key": false, "distinct_values": []}, {"name": "kho", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Kho lưu trữ vật lý", "primary_key": false, "distinct_values": []}, {"name": "tu", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Tủ lưu trữ vật lý", "primary_key": false, "distinct_values": []}, {"name": "ngan", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Ngăn lưu trữ vật lý", "primary_key": false, "distinct_values": []}, {"name": "vi_tri", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Vị trí lưu trữ chi tiết", "primary_key": false, "distinct_values": []}, {"name": "ky_hieu", "nullable": false, "data_type": "TEXT", "constraints": [], "description": "Ký hiệu hồ sơ lưu trữ", "primary_key": false, "distinct_values": []}, {"name": "ghi_chu", "nullable": true, "data_type": "TEXT", "constraints": [], "description": "Ghi chú thêm về hồ sơ lưu trữ", "primary_key": false, "distinct_values": []}]}], "relationships": [{"type": "one_to_one", "to_column": "danh_sach_benh_nhan.so_ho_so", "from_column": "danh_sach_ho_so_luu_tru.so_ho_so"}, {"type": "one_to_one", "to_column": "danh_sach_benh_nhan.so_ho_so", "from_column": "thong_tin_benh_nhan.so_ho_so"}, {"type": "one_to_one", "to_column": "thong_tin_ho_so_luu_tru.so_benh_an", "from_column": "thong_tin_benh_nhan.so_benh_an"}]}', '37837703-56fd-48d6-bd0f-82851483a6ec'::uuid, '2026-08-17 09:10:56.253337+00:00', '2026-08-17 10:02:55.528509+00:00'),
  ('0772523a-7235-410b-8eea-ee711baa62e0'::uuid, 'ThongtinHoSoLuuTru.csv', 'CSV', NULL, 'D:/VinAI/P-102/backend/data/uploads/0772523a-7235-410b-8eea-ee711baa62e0/ThongtinHoSoLuuTru.csv', '{"tables": [{"name": "ThongtinHoSoLuuTru", "columns": [{"name": "Số bệnh án", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Thời gian vào viện", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Ngày ra viện", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Vào từ khoa", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 8, "distinct_values": ["Khoa A7 (Nội thận - Tiết niệu)", "Khoa B9 (Tai - Mũi - Họng)", "Khoa A2 (Chấn thương chỉnh hình)", "Khoa A16 (Quốc tế)", "Khoa Khám bệnh", "Khoa Xạ trị", "Khoa B1-A (CT-Can thiệp)", "Khoa A1 (Nội tổng hợp)"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Ra từ khoa", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 8, "distinct_values": ["Khoa A7 (Nội thận - Tiết niệu)", "Khoa B9 (Tai - Mũi - Họng)", "Khoa A2 (Chấn thương chỉnh hình)", "Khoa Khám bệnh", "Khoa A16 (Quốc tế)", "Khoa B6 (Ngoại chấn thương)", "Khoa Xạ trị", "Khoa B1-A (CT-Can thiệp)"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Chẩn đoán", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 6, "distinct_values": ["Nhồi máu cơ tim cấp", "Thoát vị đĩa đệm cột sống thắt lưng", "Sỏi thận", "Đái tháo đường type 2", "Viêm xoang mạn tính", "U xơ tử cung"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Số lưu trữ", "nullable": false, "data_type": "INTEGER", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Ngày lưu trữ", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 11, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Trạng thái hồ sơ", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 2, "distinct_values": ["Hồ sơ chờ đưa vào kho", "Hồ sơ đang lưu trữ"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Kho", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 3, "distinct_values": ["Kho 2", "Kho 1", "Kho 3"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Tủ", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 3, "distinct_values": ["Tủ A", "Tủ B", "Tủ C"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Ngăn", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 5, "distinct_values": ["Ngăn 1", "Ngăn 4", "Ngăn 2", "Ngăn 5", "Ngăn 3"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Vị trí", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 9, "distinct_values": ["Kệ 1 - Hàng 4", "Kệ 3 - Hàng 5", "Kệ 3 - Hàng 6", "Kệ 3 - Hàng 2", "Kệ 4 - Hàng 7", "Kệ 4 - Hàng 5", "Kệ 2 - Hàng 2", "Kệ 2 - Hàng 1", "Kệ 4 - Hàng 4"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Ký hiệu", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Ghi chú", "nullable": true, "data_type": "TEXT", "null_count": 7, "constraints": [], "description": null, "primary_key": false, "distinct_count": 1, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": false}]}], "relationships": []}', 'acd9d877-9125-46e9-9529-ab1ee3703b4e'::uuid, '2026-08-22 09:52:59.324874+00:00', '2026-08-22 11:09:05.812887+00:00'),
  ('70949b7e-c7ff-43f0-baa9-3932c3dc0ae3'::uuid, 'Sample_Rides_Dataset.csv', 'CSV', 'Nguồn dữ liệu nạp cho dự án Dự án DWH Phân Tích Chuyến Đi & Tài Xế', 'samples/Sample_Rides_Dataset.csv', '{"tables": [{"name": "Rides", "columns": [{"name": "trip_id", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": true, "distinct_values": []}, {"name": "driver_id", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "customer_id", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "fare_amount", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "trip_status", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "pickup_time", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}]}], "relationships": []}', '9e085700-8993-4810-b20a-03a9a3a5e95a'::uuid, '2026-08-16 09:46:24.875594+00:00', '2026-08-16 09:46:24.875598+00:00'),
  ('7e621a51-f48a-53bf-927d-f415ae6c9249'::uuid, 'VIMES Patient Record - Hồ sơ lưu trữ (Export)', 'SQL', 'Bảng dữ liệu hồ sơ lưu trữ, thông tin bệnh nhân và danh sách bệnh nhân trích xuất từ hệ thống VIMES Patient Record qua kết nối SQL Server read-replica.', 'sqlserver://vimes-prod-replica.hospital.local:1433/VIMES_PatientRecord', '{"tables": [{"name": "ho_so_luu_tru", "columns": [{"name": "so_benh_an", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": true, "distinct_values": []}, {"name": "so_ho_so", "nullable": true, "data_type": "INTEGER", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "thoi_gian_vao_vien", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "ngay_ra_vien", "nullable": true, "data_type": "DATE", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "khoa_vao_ma", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "khoa_ra_ma", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "chan_doan", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "so_luu_tru", "nullable": true, "data_type": "INTEGER", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "ngay_luu_tru", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "trang_thai_ho_so_ma", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "kho_ma", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "tu_ma", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "ngan_ma", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "vi_tri", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "ky_hieu", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "ghi_chu", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}]}, {"name": "thong_tin_benh_nhan", "columns": [{"name": "so_ho_so", "nullable": true, "data_type": "INTEGER", "constraints": [], "description": null, "primary_key": true, "distinct_values": []}, {"name": "so_benh_an", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "ho_ten", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "tuoi", "nullable": true, "data_type": "INTEGER", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "gioi_tinh_ma", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "dia_chi", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "nghe_nghiep", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "doi_tuong_ma", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "loai_benh_an_ma", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}]}, {"name": "danh_sach_benh_nhan", "columns": [{"name": "so_ho_so", "nullable": true, "data_type": "INTEGER", "constraints": [], "description": null, "primary_key": true, "distinct_values": []}, {"name": "so_luu_tru", "nullable": true, "data_type": "INTEGER", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "ten_benh_nhan", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "tuoi", "nullable": true, "data_type": "INTEGER", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "gioi_tinh_ma", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "dia_chi", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "thoi_gian_vao_vien", "nullable": true, "data_type": "DATE", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "ngay_ra", "nullable": true, "data_type": "DATE", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "khoa_vao_ma", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "khoa_ra_ma", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "chan_doan", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}]}, {"name": "dm_gioi_tinh", "columns": [{"name": "ma", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": true, "distinct_values": []}, {"name": "ten_hien_thi", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}]}, {"name": "dm_khoa", "columns": [{"name": "ma_khoa", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": true, "distinct_values": []}, {"name": "ten_khoa", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}]}, {"name": "dm_doi_tuong", "columns": [{"name": "ma", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": true, "distinct_values": []}, {"name": "ten_hien_thi", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}]}, {"name": "dm_loai_benh_an", "columns": [{"name": "ma", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": true, "distinct_values": []}, {"name": "ten_hien_thi", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}]}, {"name": "dm_trang_thai_ho_so", "columns": [{"name": "ma", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": true, "distinct_values": []}, {"name": "ten_hien_thi", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}]}, {"name": "dm_kho", "columns": [{"name": "ma", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": true, "distinct_values": []}, {"name": "ten_hien_thi", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}]}, {"name": "dm_tu", "columns": [{"name": "ma", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": true, "distinct_values": []}, {"name": "kho_ma", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "ten_hien_thi", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}]}, {"name": "dm_ngan", "columns": [{"name": "ma", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": true, "distinct_values": []}, {"name": "tu_ma", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "ten_hien_thi", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}]}, {"name": "dm_nghe_nghiep", "columns": [{"name": "ma", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": true, "distinct_values": []}, {"name": "ten_hien_thi", "nullable": true, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}]}], "relationships": []}', '0999689b-6468-5316-83b1-0d376db6ff00'::uuid, '2025-11-04 02:12:00+00:00', '2026-08-16 13:28:48.128234+00:00'),
  ('0772523a-7235-410b-8eea-ee711baa62e0'::uuid, 'DanhSachBenhNhan.csv', 'CSV', NULL, 'D:/VinAI/P-102/backend/data/uploads/0772523a-7235-410b-8eea-ee711baa62e0/DanhSachBenhNhan.csv', '{"tables": [{"name": "DanhSachBenhNhan", "columns": [{"name": "Số hồ sơ", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": true, "is_unique_candidate": true}, {"name": "Số lưu trữ", "nullable": false, "data_type": "INTEGER", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Tên bệnh nhân", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Tuổi", "nullable": false, "data_type": "INTEGER", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 11, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Giới", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 2, "distinct_values": ["Nam", "Nữ"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Địa chỉ", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Thời gian vào viện", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Ngày ra", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Vào từ khoa", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 8, "distinct_values": ["Khoa A7 (Nội thận - Tiết niệu)", "Khoa B9 (Tai - Mũi - Họng)", "Khoa A2 (Chấn thương chỉnh hình)", "Khoa A16 (Quốc tế)", "Khoa Khám bệnh", "Khoa Xạ trị", "Khoa B1-A (CT-Can thiệp)", "Khoa A1 (Nội tổng hợp)"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Ra từ khoa", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 8, "distinct_values": ["Khoa A7 (Nội thận - Tiết niệu)", "Khoa B9 (Tai - Mũi - Họng)", "Khoa A2 (Chấn thương chỉnh hình)", "Khoa Khám bệnh", "Khoa A16 (Quốc tế)", "Khoa B6 (Ngoại chấn thương)", "Khoa Xạ trị", "Khoa B1-A (CT-Can thiệp)"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Chẩn đoán", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 6, "distinct_values": ["Nhồi máu cơ tim cấp", "Thoát vị đĩa đệm cột sống thắt lưng", "Sỏi thận", "Đái tháo đường type 2", "Viêm xoang mạn tính", "U xơ tử cung"], "is_key_candidate": false, "is_unique_candidate": false}]}], "relationships": []}', 'd58d39af-1209-4c98-bc9b-8459bb3defe6'::uuid, '2026-08-22 09:52:59.259112+00:00', '2026-08-22 11:09:05.819759+00:00'),
  ('8dfcb679-8243-5be9-b8ee-b2bde7997277'::uuid, 'Hệ thống Quản lý Đào tạo - Sinh viên', 'EXCEL', 'File Excel tổng hợp danh sách sinh viên, điểm và trạng thái tốt nghiệp do Phòng Đào tạo cung cấp theo học kỳ.', '/uploads/edu/danh_sach_sinh_vien_2025_hk1.xlsx', '{"tables": [{"name": "students", "columns": [{"name": "student_code", "data_type": "TEXT", "constraints": [], "primary_key": true, "distinct_values": []}, {"pii": true, "name": "full_name", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "faculty_code", "data_type": "TEXT", "constraints": [], "foreign_key": {"references": "faculties.faculty_code"}, "distinct_values": []}, {"name": "admission_year", "data_type": "INTEGER", "constraints": [], "distinct_values": []}, {"name": "gpa", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "graduation_status", "data_type": "TEXT", "constraints": [], "distinct_values": []}]}, {"name": "faculties", "columns": [{"name": "faculty_code", "data_type": "TEXT", "constraints": [], "primary_key": true, "distinct_values": []}, {"name": "faculty_name", "data_type": "TEXT", "constraints": [], "distinct_values": []}]}], "relationships": [{"to": "faculties.faculty_code", "from": "students.faculty_code", "type": "many_to_one"}], "row_count_estimate": 18500}', '45072fdd-d2d0-5d67-bc7d-5f8250bf82bb'::uuid, '2025-12-02 02:00:00+00:00', '2025-12-02 02:00:00+00:00'),
  ('ef1e1ed3-a3b9-5fd0-86a5-2beec97bdf48'::uuid, 'MES - Dữ liệu sản xuất theo ca', 'JSON', 'Dữ liệu sự kiện sản xuất theo thời gian thực từ hệ thống MES, xuất theo batch JSON mỗi 15 phút.', 's3://mfg-data-lake/mes/production_events/', '{"tables": [{"name": "production_events", "columns": [{"name": "event_id", "data_type": "INTEGER", "constraints": [], "primary_key": true, "distinct_values": []}, {"name": "line_code", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "shift_code", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "planned_units", "data_type": "INTEGER", "constraints": [], "distinct_values": []}, {"name": "produced_units", "data_type": "INTEGER", "constraints": [], "distinct_values": []}, {"name": "defect_units", "data_type": "INTEGER", "constraints": [], "distinct_values": []}, {"name": "downtime_minutes", "data_type": "INTEGER", "constraints": [], "distinct_values": []}, {"name": "event_time", "data_type": "TEXT", "constraints": [], "distinct_values": []}]}], "relationships": [], "source_protocol": "MQTT -> batch export JSON", "row_count_estimate": 340000}', '17e2d3cb-682c-5184-be4d-954dc729419c'::uuid, '2025-12-08 06:20:00+00:00', '2025-12-08 06:20:00+00:00'),
  ('144b02e3-6867-41af-b563-096a06fd83e2'::uuid, 'Sample_Rides_Dataset.csv', 'CSV', 'Nguồn dữ liệu nạp cho dự án Dự án DWH Phân Tích Chuyến Đi & Tài Xế', 'samples/Sample_Rides_Dataset.csv', '{"tables": [{"name": "Rides", "columns": [{"name": "trip_id", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": true, "distinct_values": []}, {"name": "driver_id", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "customer_id", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "fare_amount", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "trip_status", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "pickup_time", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}]}], "relationships": []}', '0e86cf7a-e6e9-4cd7-88f1-6862138980b0'::uuid, '2026-08-16 09:27:57.423025+00:00', '2026-08-16 09:27:57.423031+00:00'),
  ('ae94fe31-2a34-4652-a9ed-03d154eba768'::uuid, 'Sample_Rides_Dataset.csv', 'CSV', 'Nguồn dữ liệu nạp cho dự án Dự án DWH Phân Tích Chuyến Đi & Tài Xế', 'samples/Sample_Rides_Dataset.csv', '{"tables": [{"name": "Rides", "columns": [{"name": "trip_id", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": true, "distinct_values": []}, {"name": "driver_id", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "customer_id", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "fare_amount", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "trip_status", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "pickup_time", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}]}], "relationships": []}', 'eba629c1-e263-4e8c-9105-fd3fce2a5e3e'::uuid, '2026-08-16 09:39:22.014205+00:00', '2026-08-16 09:39:22.014211+00:00'),
  ('18525676-8c6b-552b-8de7-a50899ef4b92'::uuid, 'TMS - Hệ thống quản lý vận tải', 'SQL', 'Kết nối tới hệ thống Transportation Management System (PostgreSQL) lấy dữ liệu vận đơn và đối tác vận chuyển.', 'postgresql://tms-db.logistics.local:5432/tms_prod', '{"tables": [{"name": "shipments", "columns": [{"name": "shipment_id", "data_type": "TEXT", "constraints": [], "primary_key": true, "distinct_values": []}, {"name": "route_code", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "carrier_id", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "origin_hub", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "dest_hub", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "pickup_time", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "delivered_time", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "sla_hours", "data_type": "INTEGER", "constraints": [], "distinct_values": []}, {"name": "status", "data_type": "TEXT", "constraints": [], "distinct_values": []}]}, {"name": "carriers", "columns": [{"name": "carrier_id", "data_type": "TEXT", "constraints": [], "primary_key": true, "distinct_values": []}, {"name": "carrier_name", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "vehicle_type", "data_type": "TEXT", "constraints": [], "distinct_values": []}]}], "relationships": [{"to": "carriers.carrier_id", "from": "shipments.carrier_id", "type": "many_to_one"}], "row_count_estimate": 890000}', 'db01c8cc-3651-5089-bd1f-d07ff5d7deb4'::uuid, '2025-11-18 04:20:00+00:00', '2025-11-18 04:20:00+00:00'),
  ('53774151-12ea-53d4-9d34-ebccfd4a2594'::uuid, 'Hệ thống Hợp đồng & Bồi thường', 'SQL', 'Trích xuất dữ liệu hợp đồng bảo hiểm và hồ sơ yêu cầu bồi thường từ hệ thống lõi bảo hiểm.', 'sqlserver://policy-core.insureco.vn:1433/PolicyCore', '{"tables": [{"name": "policies", "columns": [{"name": "policy_no", "data_type": "TEXT", "constraints": [], "primary_key": true, "distinct_values": []}, {"name": "product_code", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"pii": true, "name": "holder_name", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "sum_assured", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "issue_date", "data_type": "DATE", "constraints": [], "distinct_values": []}]}, {"name": "claims", "columns": [{"name": "claim_id", "data_type": "TEXT", "constraints": [], "primary_key": true, "distinct_values": []}, {"name": "policy_no", "data_type": "TEXT", "constraints": [], "foreign_key": {"references": "policies.policy_no"}, "distinct_values": []}, {"name": "claim_amount", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "claim_status", "data_type": "TEXT", "constraints": [], "distinct_values": []}, {"name": "filed_date", "data_type": "DATE", "constraints": [], "distinct_values": []}, {"name": "is_suspected_fraud", "data_type": "BOOLEAN", "constraints": [], "distinct_values": []}]}], "relationships": [{"to": "policies.policy_no", "from": "claims.policy_no", "type": "many_to_one"}], "row_count_estimate": 210000}', 'eea70fb1-adaa-5b4c-a360-9fe710e5e011'::uuid, '2025-10-20 01:20:00+00:00', '2025-10-20 01:20:00+00:00'),
  ('29e97dc3-2e93-4430-9a12-9b3992541f31'::uuid, 'Sample_Rides_Dataset.csv', 'CSV', 'Nguồn dữ liệu nạp cho dự án Dự án DWH Phân Tích Chuyến Đi & Tài Xế', 'samples/Sample_Rides_Dataset.csv', '{"tables": [{"name": "Rides", "columns": [{"name": "trip_id", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": true, "distinct_values": []}, {"name": "driver_id", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "customer_id", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "fare_amount", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "trip_status", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "pickup_time", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}]}], "relationships": []}', 'fea8bb38-06cd-495e-9cd5-5a0130772bfa'::uuid, '2026-08-16 09:40:18.619664+00:00', '2026-08-16 09:40:18.619670+00:00'),
  ('7e621a51-f48a-53bf-927d-f415ae6c9249'::uuid, 'DanhSachHoSoLuuTru.csv', 'CSV', NULL, 'D:/VinAI/P-102/backend/data/uploads/7e621a51-f48a-53bf-927d-f415ae6c9249/DanhSachHoSoLuuTru.csv', '{"tables": [{"name": "DanhSachHoSoLuuTru", "columns": [{"name": "Số hồ sơ", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "Tên bệnh nhân", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "Tuổi", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "Giới", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": ["Nam", "Nữ", "Khác"]}, {"name": "Thời gian vào viện", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "Ngày ra", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "Vào từ khoa", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "Ra từ khoa", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}, {"name": "Chẩn đoán", "nullable": false, "data_type": "TEXT", "constraints": [], "description": null, "primary_key": false, "distinct_values": []}]}], "relationships": []}', 'cfb5090b-2c4b-46ac-9cf4-5f21ff0ef052'::uuid, '2026-08-16 13:28:16.088593+00:00', '2026-08-17 08:58:53.478522+00:00'),
  ('b05c0f83-d93a-439b-bb1a-f7c109af8201'::uuid, 'DanhSachBenhNhan.csv', 'CSV', NULL, 'D:/VinAI/P-102/backend/data/uploads/b05c0f83-d93a-439b-bb1a-f7c109af8201/DanhSachBenhNhan.csv', '{"tables": [{"name": "DanhSachBenhNhan", "columns": [{"name": "Số hồ sơ", "nullable": false, "data_type": "INTEGER", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": []}, {"name": "Số lưu trữ", "nullable": false, "data_type": "INTEGER", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": []}, {"name": "Tên bệnh nhân", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": []}, {"name": "Tuổi", "nullable": false, "data_type": "INTEGER", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 11, "distinct_values": []}, {"name": "Giới", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 2, "distinct_values": ["Nam", "Nữ"]}, {"name": "Địa chỉ", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": []}, {"name": "Thời gian vào viện", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": []}, {"name": "Ngày ra", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": []}, {"name": "Vào từ khoa", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 8, "distinct_values": []}, {"name": "Ra từ khoa", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 8, "distinct_values": []}, {"name": "Chẩn đoán", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 6, "distinct_values": []}]}], "relationships": []}', 'bf86a432-40f9-42b4-a499-3b6f987cd516'::uuid, '2026-08-22 02:08:07.322752+00:00', '2026-08-22 02:08:07.322793+00:00'),
  ('0772523a-7235-410b-8eea-ee711baa62e0'::uuid, 'DanhSachHoSoLuuTru.csv', 'CSV', NULL, 'D:/VinAI/P-102/backend/data/uploads/0772523a-7235-410b-8eea-ee711baa62e0/DanhSachHoSoLuuTru.csv', '{"tables": [{"name": "DanhSachHoSoLuuTru", "columns": [{"name": "Số hồ sơ", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": true, "is_unique_candidate": true}, {"name": "Tên bệnh nhân", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Tuổi", "nullable": false, "data_type": "INTEGER", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 11, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Giới", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 2, "distinct_values": ["Nam", "Nữ"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Thời gian vào viện", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Ngày ra", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 12, "distinct_values": [], "is_key_candidate": false, "is_unique_candidate": true}, {"name": "Vào từ khoa", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 8, "distinct_values": ["Khoa A7 (Nội thận - Tiết niệu)", "Khoa B9 (Tai - Mũi - Họng)", "Khoa A2 (Chấn thương chỉnh hình)", "Khoa A16 (Quốc tế)", "Khoa Khám bệnh", "Khoa Xạ trị", "Khoa B1-A (CT-Can thiệp)", "Khoa A1 (Nội tổng hợp)"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Ra từ khoa", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 8, "distinct_values": ["Khoa A7 (Nội thận - Tiết niệu)", "Khoa B9 (Tai - Mũi - Họng)", "Khoa A2 (Chấn thương chỉnh hình)", "Khoa Khám bệnh", "Khoa A16 (Quốc tế)", "Khoa B6 (Ngoại chấn thương)", "Khoa Xạ trị", "Khoa B1-A (CT-Can thiệp)"], "is_key_candidate": false, "is_unique_candidate": false}, {"name": "Chẩn đoán", "nullable": false, "data_type": "TEXT", "null_count": 0, "constraints": [], "description": null, "primary_key": false, "distinct_count": 6, "distinct_values": ["Nhồi máu cơ tim cấp", "Thoát vị đĩa đệm cột sống thắt lưng", "Sỏi thận", "Đái tháo đường type 2", "Viêm xoang mạn tính", "U xơ tử cung"], "is_key_candidate": false, "is_unique_candidate": false}]}], "relationships": []}', '3c47fb8a-e051-43bb-96c2-117c79f74194'::uuid, '2026-08-22 09:52:59.291609+00:00', '2026-08-22 11:09:05.828924+00:00')
ON CONFLICT DO NOTHING;

-- Data for: data_models (13 rows)
INSERT INTO "data_models" ("project_id", "dbml", "revision", "id", "created_at", "updated_at", "generated_from_requirement_revision", "generated_from_source_revision") VALUES
  ('84bdeb46-0eba-564e-8437-833ede4e2718'::uuid, 'Table dim_khoa {
  khoa_key varchar(10) [pk]
  ten_khoa varchar(100)
}

Table dim_chan_doan {
  chan_doan_key uuid [pk]
  ten_chan_doan varchar(250)
  nhom_chan_doan varchar(100)
}

Table dim_doi_tuong {
  doi_tuong_key varchar(20) [pk]
  ten_doi_tuong varchar(50)
}

Table dim_date {
  date_key date [pk]
  nam integer
  quy integer
  thang integer
}

Table fact_luot_kham {
  luot_kham_key uuid [pk]
  khoa_vao_key varchar(10) [ref: > dim_khoa.khoa_key]
  khoa_ra_key varchar(10) [ref: > dim_khoa.khoa_key]
  chan_doan_key uuid [ref: > dim_chan_doan.chan_doan_key]
  doi_tuong_key varchar(20) [ref: > dim_doi_tuong.doi_tuong_key]
  ngay_vao_key date [ref: > dim_date.date_key]
  so_luot integer
}
', 1, 'f0cfe13c-7110-5ffe-bfc6-7bd37be7e8b8'::uuid, '2025-12-10 05:00:00+00:00', '2025-12-10 05:00:00+00:00', 1, 1),
  ('b2f95613-a6f8-5e35-b6d7-e03bf1cc7aae'::uuid, 'Table dim_customer {
  customer_key bigint [pk]
  segment varchar(30)
  risk_score integer
  kyc_status varchar(20)
}

Table dim_account {
  account_key varchar(20) [pk]
  customer_key bigint [ref: > dim_customer.customer_key]
  account_type varchar(20)
}

Table dim_channel {
  channel_key varchar(20) [pk]
  channel_name varchar(50)
}

Table dim_date {
  date_key date [pk]
  nam integer
  thang integer
  ngay integer
}

Table fact_transaction {
  transaction_key bigint [pk]
  account_key varchar(20) [ref: > dim_account.account_key]
  channel_key varchar(20) [ref: > dim_channel.channel_key]
  date_key date [ref: > dim_date.date_key]
  amount numeric(18,2)
  is_flagged boolean
}
', 2, '669b488c-5595-518f-a10b-2d02e1561333'::uuid, '2025-11-08 05:35:00+00:00', '2026-08-05 07:10:00+00:00', 1, 1),
  ('54505703-ca04-5613-9f4a-d2499f12ee3d'::uuid, 'Table dim_sku {
  sku_key varchar(30) [pk]
  category varchar(50)
  brand varchar(50)
}

Table dim_store {
  store_key varchar(10) [pk]
  region varchar(50)
  store_type varchar(30)
}

Table dim_date {
  date_key date [pk]
  nam integer
  tuan integer
}

Table fact_doanh_thu_ban_hang {
  invoice_line_key uuid [pk]
  sku_key varchar(30) [ref: > dim_sku.sku_key]
  store_key varchar(10) [ref: > dim_store.store_key]
  date_key date [ref: > dim_date.date_key]
  qty integer
  revenue numeric(14,2)
  discount_amount numeric(14,2)
}
', 1, 'a42297a7-08d0-592a-b70a-8409a153ff05'::uuid, '2025-11-11 04:56:00+00:00', '2025-11-11 04:56:00+00:00', 1, 1),
  ('18525676-8c6b-552b-8de7-a50899ef4b92'::uuid, 'Table dim_route {
  route_key varchar(20) [pk]
  origin_hub varchar(50)
  dest_hub varchar(50)
}

Table dim_carrier {
  carrier_key varchar(20) [pk]
  carrier_name varchar(100)
  vehicle_type varchar(30)
}

Table dim_date {
  date_key date [pk]
  nam integer
  thang integer
}

Table fact_shipment {
  shipment_key varchar(30) [pk]
  route_key varchar(20) [ref: > dim_route.route_key]
  carrier_key varchar(20) [ref: > dim_carrier.carrier_key]
  date_key date [ref: > dim_date.date_key]
  sla_hours integer
  actual_hours numeric(6,2)
  is_on_time boolean
}
', 2, '26d054de-06b0-51ca-86d3-270a75cc88f3'::uuid, '2025-11-18 06:25:00+00:00', '2025-11-20 02:00:00+00:00', 1, 1),
  ('8dfcb679-8243-5be9-b8ee-b2bde7997277'::uuid, 'Table dim_faculty {
  faculty_key varchar(10) [pk]
  faculty_name varchar(100)
}

Table dim_student {
  student_key varchar(15) [pk]
  faculty_key varchar(10) [ref: > dim_faculty.faculty_key]
  admission_year integer
}

Table fact_ket_qua_hoc_tap {
  record_key uuid [pk]
  student_key varchar(15) [ref: > dim_student.student_key]
  gpa numeric(3,2)
  graduation_status varchar(20)
}
', 1, '2cc82e1c-0bd2-53bf-9574-29360fa77708'::uuid, '2025-12-02 03:45:00+00:00', '2025-12-02 03:45:00+00:00', 1, 1),
  ('ef1e1ed3-a3b9-5fd0-86a5-2beec97bdf48'::uuid, 'Table dim_line {
  line_key varchar(10) [pk]
  line_name varchar(50)
}

Table dim_shift {
  shift_key varchar(5) [pk]
  shift_name varchar(30)
}

Table fact_production {
  event_key bigint [pk]
  line_key varchar(10) [ref: > dim_line.line_key]
  shift_key varchar(5) [ref: > dim_shift.shift_key]
  planned_units integer
  produced_units integer
  defect_units integer
  downtime_minutes integer
  availability numeric(5,4)
  performance numeric(5,4)
  quality numeric(5,4)
  oee numeric(5,4)
}
', 1, '353a2d9e-ab98-5c99-b541-5a168aa5b332'::uuid, '2025-12-08 08:50:00+00:00', '2025-12-08 08:50:00+00:00', 1, 1),
  ('53774151-12ea-53d4-9d34-ebccfd4a2594'::uuid, 'Table dim_product {
  product_key varchar(10) [pk]
  product_name varchar(100)
}

Table dim_policy {
  policy_key varchar(20) [pk]
  product_key varchar(10) [ref: > dim_product.product_key]
}

Table fact_claim {
  claim_key varchar(20) [pk]
  policy_key varchar(20) [ref: > dim_policy.policy_key]
  claim_amount numeric(18,2)
  claim_status varchar(20)
  is_suspected_fraud boolean
}
', 1, '393a9c32-6723-514e-84bc-d6fa875157bf'::uuid, '2025-10-20 02:00:00+00:00', '2025-10-20 02:00:00+00:00', 1, 1),
  ('f8c4432f-0252-5275-a581-958039b98639'::uuid, 'Table dim_subscriber {
  subscriber_key varchar(15) [pk]
  plan_key varchar(10)
  region varchar(30)
  status varchar(15)
}

Table dim_plan {
  plan_key varchar(10) [pk]
  plan_name varchar(50)
}

Table dim_date {
  date_key date [pk]
  nam integer
  thang integer
}

Table fact_usage_monthly {
  usage_key uuid [pk]
  subscriber_key varchar(15) [ref: > dim_subscriber.subscriber_key]
  date_key date [ref: > dim_date.date_key]
  total_data_mb numeric(14,2)
  total_voice_minutes numeric(12,2)
  arpu numeric(12,2)
  is_churned boolean
}
', 2, 'c68e1dd1-f2d4-50bd-bd34-9743e6d79968'::uuid, '2025-12-15 05:20:00+00:00', '2025-12-18 02:00:00+00:00', 1, 1),
  ('6268eced-f86b-5e52-b0a9-262a806879e9'::uuid, 'Table dim_category {
  category_key varchar(30) [pk]
  category_name varchar(100)
}

Table dim_channel {
  channel_key varchar(20) [pk]
  channel_name varchar(50)
}

Table fact_cart_funnel {
  event_key uuid [pk]
  category_key varchar(30) [ref: > dim_category.category_key]
  channel_key varchar(20) [ref: > dim_channel.channel_key]
  add_to_cart_count integer
  checkout_count integer
  purchase_count integer
}

Table fact_ad_spend {
  campaign_key varchar(20) [pk]
  channel_key varchar(20) [ref: > dim_channel.channel_key]
  spend numeric(14,2)
  conversions integer
}
', 1, '97998605-51ac-53da-8391-89e07a426729'::uuid, '2026-01-05 06:05:00+00:00', '2026-01-05 06:05:00+00:00', 1, 1),
  ('7e621a51-f48a-53bf-927d-f415ae6c9249'::uuid, 'Table "dim_benh_nhan" {
  "benh_nhan_key" uuid [pk]
  "so_ho_so_hash" varchar(64) [note: ''SHA-256 của so_ho_so, dùng để truy vết'']
  "tuoi" integer
  "gioi_tinh" varchar(10)
  "nhom_tuoi" varchar(20)
  "doi_tuong_chi_tra" varchar(50)
  "nghe_nghiep" varchar(50)
}

Table "dim_khoa" {
  "khoa_key" varchar(10) [pk]
  "ten_khoa" varchar(100)
}

Table "dim_vi_tri_luu_tru" {
  "vi_tri_key" uuid [pk]
  "kho" varchar(50)
  "tu" varchar(50)
  "ngan" varchar(50)
  "suc_chua" integer
}

Table "dim_trang_thai_ho_so" {
  "trang_thai_key" varchar(10) [pk]
  "ten_trang_thai" varchar(50)
}

Table "dim_date" {
  "date_key" date [pk]
  "nam" integer
  "quy" integer
  "thang" "timestamp with time zone"
}

Table "dim_loai_benh_an" {
  "loai_key" varchar(10) [pk]
  "ten_loai" varchar(100)
}

Table "fact_ho_so_luu_tru" {
  "so_benh_an" varchar(30) [pk]
  "benh_nhan_key" uuid
  "khoa_vao_key" varchar(10)
  "khoa_ra_key" varchar(10)
  "vi_tri_key" uuid
  "trang_thai_key" varchar(10)
  "loai_key" varchar(10)
  "ngay_vao_key" date
  "ngay_ra_key" date
  "ngay_luu_tru_key" date
  "so_ngay_dieu_tri" integer
  "so_ngay_den_khi_luu_tru" integer
}

Ref:"dim_benh_nhan"."benh_nhan_key" < "fact_ho_so_luu_tru"."benh_nhan_key"

Ref:"dim_khoa"."khoa_key" < "fact_ho_so_luu_tru"."khoa_vao_key"

Ref:"dim_khoa"."khoa_key" < "fact_ho_so_luu_tru"."khoa_ra_key"

Ref:"dim_vi_tri_luu_tru"."vi_tri_key" < "fact_ho_so_luu_tru"."vi_tri_key"

Ref:"dim_trang_thai_ho_so"."trang_thai_key" < "fact_ho_so_luu_tru"."trang_thai_key"

Ref:"dim_loai_benh_an"."loai_key" < "fact_ho_so_luu_tru"."loai_key"

Ref:"dim_date"."date_key" < "fact_ho_so_luu_tru"."ngay_vao_key"

Ref:"dim_date"."date_key" < "fact_ho_so_luu_tru"."ngay_ra_key"

Ref:"dim_date"."date_key" < "fact_ho_so_luu_tru"."ngay_luu_tru_key"
', 4, '334a17ab-5a72-55be-9df9-5fd337c22a6c'::uuid, '2025-11-04 04:50:00+00:00', '2026-08-16 13:31:58.912593+00:00', 1, 1),
  ('0baed64b-d380-4a01-a64b-265af7059568'::uuid, 'Table Dim_Benh_Nhan {
  benh_nhan_key int [pk, increment]
  so_ho_so_natural_id int
  ten_benh_nhan varchar
  tuoi int
  gioi_tinh varchar
  dia_chi varchar
  nghe_nghiep varchar
  doi_tuong varchar
  loai varchar
}

Table Dim_Khoa {
  khoa_key int [pk, increment]
  ten_khoa varchar
}

Table Dim_Vi_Tri_Luu_Tru {
  vi_tri_luu_tru_key int [pk, increment]
  kho varchar
  tu varchar
  ngan varchar
  vi_tri varchar
  ky_hieu varchar
}

Table Dim_Trang_Thai_Ho_So {
  trang_thai_ho_so_key int [pk, increment]
  trang_thai_ho_so varchar
}

Table Dim_Date {
  date_key int [pk]
  full_date date
  day int
  month int
  year int
}

Table Fact_Dieu_Tri {
  dieu_tri_key int [pk, increment]
  benh_nhan_key int [not null, ref: > Dim_Benh_Nhan.benh_nhan_key]
  khoa_vao_key int [not null, ref: > Dim_Khoa.khoa_key]
  khoa_ra_key int [not null, ref: > Dim_Khoa.khoa_key]
  ngay_vao_key int [not null, ref: > Dim_Date.date_key]
  ngay_ra_key int [not null, ref: > Dim_Date.date_key]
  so_benh_an varchar
  chan_doan text
  thoi_gian_dieu_tri_ngay int
  so_luong_tiep_nhan int
}

Table Fact_Ho_So_Luu_Tru {
  ho_so_luu_tru_key int [pk, increment]
  benh_nhan_key int [not null, ref: > Dim_Benh_Nhan.benh_nhan_key]
  vi_tri_luu_tru_key int [not null, ref: > Dim_Vi_Tri_Luu_Tru.vi_tri_luu_tru_key]
  trang_thai_ho_so_key int [not null, ref: > Dim_Trang_Thai_Ho_So.trang_thai_ho_so_key]
  ngay_luu_tru_key int [not null, ref: > Dim_Date.date_key]
  so_luu_tru int
  ghi_chu text
  so_luong_ho_so int
}', 1, '437b69f6-2867-4377-a0be-85eb8f42d7d3'::uuid, '2026-08-17 10:02:55.537295+00:00', '2026-08-17 10:02:55.537298+00:00', 1, 1),
  ('0772523a-7235-410b-8eea-ee711baa62e0'::uuid, 'Table "Dim_BenhNhan" {
  "BenhNhan_Key" integer [pk, increment]
  "SoHoSo" varchar(50) [not null]
  "HoTen" varchar(255)
  "GioiTinh" varchar(20)
  "DiaChi" varchar(255)
  "NgheNghiep" varchar(100)
  "DoiTuong" varchar(100)
  "LoaiDieuTri" varchar(100)
}

Table "Dim_KhoaPhong" {
  "Khoa_Key" integer [pk, increment]
  "TenKhoa" varchar(255) [not null]
}

Table "Dim_ChanDoan" {
  "ChanDoan_Key" integer [pk, increment]
  "TenChanDoan" varchar(255) [not null]
}

Table "Dim_ViTriLuuTru" {
  "ViTri_Key" integer [pk, increment]
  "Kho" varchar(100)
  "Tu" varchar(100)
  "Ngan" varchar(100)
  "ViTriChiTiet" varchar(100)
}

Table "Dim_TrangThaiHoSo" {
  "TrangThai_Key" integer [pk, increment]
  "TenTrangThai" varchar(100) [not null]
}

Table "Dim_Date" {
  "Date_Key" integer [pk]
  "FullDate" date [not null]
  "Day" integer
  "Month" integer
  "Quarter" integer
  "Year" integer
}

Table "Fact_DieuTri" {
  "Fact_DieuTri_Key" bigint [pk, increment]
  "BenhNhan_Key" integer [not null]
  "KhoaVao_Key" integer [not null]
  "KhoaRa_Key" integer [not null]
  "ChanDoan_Key" integer [not null]
  "NgayVao_Key" integer [not null]
  "NgayRa_Key" integer [not null]
  "Tuoi" integer
  "ThoiGianVaoVien" datetime
  "NgayRaVien" datetime
  "SoNgayDieuTri" numeric(10,2)
}

Table "Fact_LuuTruHoSo" {
  "Fact_LuuTru_Key" bigint [pk, increment]
  "BenhNhan_Key" integer [not null]
  "ViTri_Key" integer [not null]
  "TrangThai_Key" integer [not null]
  "ChanDoan_Key" integer [not null]
  "NgayLuuTru_Key" integer [not null]
  "SoBenhAn" varchar(50)
  "SoLuuTru" integer
  "KyHieu" varchar(100)
  "GhiChu" text
  "SoLuongHoSo" integer
}

Ref: "Fact_DieuTri"."BenhNhan_Key" > "Dim_BenhNhan"."BenhNhan_Key"
Ref: "Fact_DieuTri"."KhoaVao_Key" > "Dim_KhoaPhong"."Khoa_Key"
Ref: "Fact_DieuTri"."KhoaRa_Key" > "Dim_KhoaPhong"."Khoa_Key"
Ref: "Fact_DieuTri"."ChanDoan_Key" > "Dim_ChanDoan"."ChanDoan_Key"
Ref: "Fact_DieuTri"."NgayVao_Key" > "Dim_Date"."Date_Key"
Ref: "Fact_DieuTri"."NgayRa_Key" > "Dim_Date"."Date_Key"

Ref: "Fact_LuuTruHoSo"."BenhNhan_Key" > "Dim_BenhNhan"."BenhNhan_Key"
Ref: "Fact_LuuTruHoSo"."ViTri_Key" > "Dim_ViTriLuuTru"."ViTri_Key"
Ref: "Fact_LuuTruHoSo"."TrangThai_Key" > "Dim_TrangThaiHoSo"."TrangThai_Key"
Ref: "Fact_LuuTruHoSo"."ChanDoan_Key" > "Dim_ChanDoan"."ChanDoan_Key"
Ref: "Fact_LuuTruHoSo"."NgayLuuTru_Key" > "Dim_Date"."Date_Key"', 4, '11ec29ff-332c-4dbe-824c-f9390fb8e8cb'::uuid, '2026-08-22 11:13:34.593740+00:00', '2026-08-22 18:50:44.006732+00:00', 1, 1),
  ('2da8c727-32f8-4ce2-9528-ae87ee60077d'::uuid, 'Table "Dim_Date" {
  "date_key" integer [pk]
  "full_date" date
  "day" integer
  "month" integer
  "quarter" integer
  "year" integer
}

Table "Dim_BenhNhan" {
  "patient_key" integer [pk]
  "so_ho_so" varchar
  "so_benh_an" varchar
  "tuoi" integer
  "gioi_tinh" varchar
  "nghe_nghiep" varchar
  "doi_tuong_chi_tra" varchar
  "loai_dieu_tri" varchar
}

Table "Dim_Khoa" {
  "khoa_key" integer [pk]
  "ten_khoa" varchar
}

Table "Dim_ChanDoan" {
  "chan_doan_key" integer [pk]
  "ten_chan_doan" varchar
}

Table "Dim_ViTriLuuTru" {
  "vi_tri_key" integer [pk]
  "kho" varchar
  "tu" varchar
  "ngan" varchar
  "vi_tri_ke" varchar
  "ky_hieu" varchar
}

Table "Dim_TrangThaiHoSo" {
  "trang_thai_key" integer [pk]
  "ten_trang_thai" varchar
}

Table "Fact_KhamChuaBenh" {
  "kham_chua_benh_key" integer [pk]
  "patient_key" integer
  "vao_khoa_key" integer
  "ra_khoa_key" integer
  "chan_doan_key" integer
  "ngay_vao_key" integer
  "ngay_ra_key" integer
  "thoi_gian_dieu_tri_ngay" integer
  "so_luong_luot_kham" integer
}

Table "Fact_HoSoLuuTru" {
  "ho_so_luu_tru_key" integer [pk]
  "patient_key" integer
  "vi_tri_key" integer
  "trang_thai_key" integer
  "ngay_luu_tru_key" integer
  "so_luu_tru" integer
  "ghi_chu" varchar
  "so_luong_ho_so" integer
}

Ref: "Fact_KhamChuaBenh"."patient_key" > "Dim_BenhNhan"."patient_key"
Ref: "Fact_KhamChuaBenh"."vao_khoa_key" > "Dim_Khoa"."khoa_key"
Ref: "Fact_KhamChuaBenh"."ra_khoa_key" > "Dim_Khoa"."khoa_key"
Ref: "Fact_KhamChuaBenh"."chan_doan_key" > "Dim_ChanDoan"."chan_doan_key"
Ref: "Fact_KhamChuaBenh"."ngay_vao_key" > "Dim_Date"."date_key"
Ref: "Fact_KhamChuaBenh"."ngay_ra_key" > "Dim_Date"."date_key"
Ref: "Fact_HoSoLuuTru"."patient_key" > "Dim_BenhNhan"."patient_key"
Ref: "Fact_HoSoLuuTru"."vi_tri_key" > "Dim_ViTriLuuTru"."vi_tri_key"
Ref: "Fact_HoSoLuuTru"."trang_thai_key" > "Dim_TrangThaiHoSo"."trang_thai_key"
Ref: "Fact_HoSoLuuTru"."ngay_luu_tru_key" > "Dim_Date"."date_key"', 5, 'd7474a47-743b-4351-9bd9-a35e9933ca3c'::uuid, '2026-08-23 12:24:05.919212+00:00', '2026-08-23 12:44:24.614727+00:00', 1, 3)
ON CONFLICT DO NOTHING;

-- Data for: data_model_changes (17 rows)
INSERT INTO "data_model_changes" ("data_model_id", "base_revision", "proposed_dbml", "status", "user_id", "id", "created_at", "updated_at", "base_dbml") VALUES
  ('334a17ab-5a72-55be-9df9-5fd337c22a6c'::uuid, 1, 'Table dim_benh_nhan {
  benh_nhan_key uuid [pk]
  so_ho_so_hash varchar(64) [note: ''SHA-256 của so_ho_so, dùng để truy vết'']
  tuoi integer
  gioi_tinh varchar(10)
  nhom_tuoi varchar(20)
  doi_tuong_chi_tra varchar(50)
  nghe_nghiep varchar(50)
}

Table dim_khoa {
  khoa_key varchar(10) [pk]
  ten_khoa varchar(100)
}

Table dim_vi_tri_luu_tru {
  vi_tri_key uuid [pk]
  kho varchar(50)
  tu varchar(50)
  ngan varchar(50)
  suc_chua integer
}

Table dim_trang_thai_ho_so {
  trang_thai_key varchar(10) [pk]
  ten_trang_thai varchar(50)
}

Table dim_date {
  date_key date [pk]
  nam integer
  quy integer
  thang integer
}

Table dim_loai_benh_an {
  loai_key varchar(10) [pk]
  ten_loai varchar(100)
}

Table fact_ho_so_luu_tru {
  // v2: bổ sung so_ngay_den_khi_luu_tru
  so_benh_an varchar(30) [pk]
  benh_nhan_key uuid [ref: > dim_benh_nhan.benh_nhan_key]
  khoa_vao_key varchar(10) [ref: > dim_khoa.khoa_key]
  khoa_ra_key varchar(10) [ref: > dim_khoa.khoa_key]
  vi_tri_key uuid [ref: > dim_vi_tri_luu_tru.vi_tri_key]
  trang_thai_key varchar(10) [ref: > dim_trang_thai_ho_so.trang_thai_key]
  loai_key varchar(10) [ref: > dim_loai_benh_an.loai_key]
  ngay_vao_key date [ref: > dim_date.date_key]
  ngay_ra_key date [ref: > dim_date.date_key]
  ngay_luu_tru_key date [ref: > dim_date.date_key]
  so_ngay_dieu_tri integer
  so_ngay_den_khi_luu_tru integer
}
', 'ACCEPTED', '15c1be82-ea36-5205-af17-7fb5947c2027'::uuid, '22906d5d-30f7-59bc-abf1-2ddb3c25dc04'::uuid, '2025-11-04 07:00:00+00:00', '2025-11-04 08:30:00+00:00', 'Table "dim_benh_nhan" {
  "benh_nhan_key" uuid [pk]
  "so_ho_so_hash" varchar(64) [note: ''SHA-256 của so_ho_so, dùng để truy vết'']
  "tuoi" integer
  "gioi_tinh" varchar(10)
  "nhom_tuoi" varchar(20)
  "doi_tuong_chi_tra" varchar(50)
  "nghe_nghiep" varchar(50)
}

Table "dim_khoa" {
  "khoa_key" varchar(10) [pk]
  "ten_khoa" varchar(100)
}

Table "dim_vi_tri_luu_tru" {
  "vi_tri_key" uuid [pk]
  "kho" varchar(50)
  "tu" varchar(50)
  "ngan" varchar(50)
  "suc_chua" integer
}

Table "dim_trang_thai_ho_so" {
  "trang_thai_key" varchar(10) [pk]
  "ten_trang_thai" varchar(50)
}

Table "dim_date" {
  "date_key" date [pk]
  "nam" integer
  "quy" integer
  "thang" "timestamp with time zone"
}

Table "dim_loai_benh_an" {
  "loai_key" varchar(10) [pk]
  "ten_loai" varchar(100)
}

Table "fact_ho_so_luu_tru" {
  "so_benh_an" varchar(30) [pk]
  "benh_nhan_key" uuid
  "khoa_vao_key" varchar(10)
  "khoa_ra_key" varchar(10)
  "vi_tri_key" uuid
  "trang_thai_key" varchar(10)
  "loai_key" varchar(10)
  "ngay_vao_key" date
  "ngay_ra_key" date
  "ngay_luu_tru_key" date
  "so_ngay_dieu_tri" integer
  "so_ngay_den_khi_luu_tru" integer
}

Ref:"dim_benh_nhan"."benh_nhan_key" < "fact_ho_so_luu_tru"."benh_nhan_key"

Ref:"dim_khoa"."khoa_key" < "fact_ho_so_luu_tru"."khoa_vao_key"

Ref:"dim_khoa"."khoa_key" < "fact_ho_so_luu_tru"."khoa_ra_key"

Ref:"dim_vi_tri_luu_tru"."vi_tri_key" < "fact_ho_so_luu_tru"."vi_tri_key"

Ref:"dim_trang_thai_ho_so"."trang_thai_key" < "fact_ho_so_luu_tru"."trang_thai_key"

Ref:"dim_loai_benh_an"."loai_key" < "fact_ho_so_luu_tru"."loai_key"

Ref:"dim_date"."date_key" < "fact_ho_so_luu_tru"."ngay_vao_key"

Ref:"dim_date"."date_key" < "fact_ho_so_luu_tru"."ngay_ra_key"

Ref:"dim_date"."date_key" < "fact_ho_so_luu_tru"."ngay_luu_tru_key"
'),
  ('2cc82e1c-0bd2-53bf-9574-29360fa77708'::uuid, 1, 'Table dim_faculty {
  faculty_key varchar(10) [pk]
  faculty_name varchar(100)
}

Table dim_student {
  student_key varchar(15) [pk]
  faculty_key varchar(10) [ref: > dim_faculty.faculty_key]
  admission_year integer
}

Table fact_ket_qua_hoc_tap {
  record_key uuid [pk]
  student_key varchar(15) [ref: > dim_student.student_key]
  gpa numeric(3,2)
  graduation_status varchar(20)
}

// đề xuất: thêm fact_hoc_phi
', 'PROPOSED', '729525be-38aa-50fd-8ea9-3fedf76615f1'::uuid, '9cbd88d1-47f2-5740-a897-5f366032338d'::uuid, '2025-12-03 03:00:00+00:00', '2025-12-03 03:00:00+00:00', 'Table dim_faculty {
  faculty_key varchar(10) [pk]
  faculty_name varchar(100)
}

Table dim_student {
  student_key varchar(15) [pk]
  faculty_key varchar(10) [ref: > dim_faculty.faculty_key]
  admission_year integer
}

Table fact_ket_qua_hoc_tap {
  record_key uuid [pk]
  student_key varchar(15) [ref: > dim_student.student_key]
  gpa numeric(3,2)
  graduation_status varchar(20)
}
'),
  ('334a17ab-5a72-55be-9df9-5fd337c22a6c'::uuid, 2, 'Table dim_benh_nhan {
  benh_nhan_key uuid [pk]
  so_ho_so_hash varchar(64) [note: ''SHA-256 của so_ho_so, dùng để truy vết'']
  tuoi integer
  gioi_tinh varchar(10)
  nhom_tuoi varchar(20)
  doi_tuong_chi_tra varchar(50)
  nghe_nghiep varchar(50)
}

Table dim_khoa {
  khoa_key varchar(10) [pk]
  ten_khoa varchar(100)
}

Table dim_vi_tri_luu_tru {
  vi_tri_key uuid [pk]
  kho varchar(50)
  tu varchar(50)
  ngan varchar(50)
  suc_chua integer
}

Table dim_trang_thai_ho_so {
  trang_thai_key varchar(10) [pk]
  ten_trang_thai varchar(50)
}

Table dim_date {
  date_key date [pk]
  nam integer
  quy integer
  thang integer
}

Table dim_loai_benh_an {
  loai_key varchar(10) [pk]
  ten_loai varchar(100)
}

Table fact_ho_so_luu_tru {
  so_benh_an varchar(30) [pk]
  benh_nhan_key uuid [ref: > dim_benh_nhan.benh_nhan_key]
  khoa_vao_key varchar(10) [ref: > dim_khoa.khoa_key]
  khoa_ra_key varchar(10) [ref: > dim_khoa.khoa_key]
  vi_tri_key uuid [ref: > dim_vi_tri_luu_tru.vi_tri_key]
  trang_thai_key varchar(10) [ref: > dim_trang_thai_ho_so.trang_thai_key]
  loai_key varchar(10) [ref: > dim_loai_benh_an.loai_key]
  ngay_vao_key date [ref: > dim_date.date_key]
  ngay_ra_key date [ref: > dim_date.date_key]
  ngay_luu_tru_key date [ref: > dim_date.date_key]
  so_ngay_dieu_tri integer
  so_ngay_den_khi_luu_tru integer
}

// v3: bổ sung fact_ton_kho_vi_tri cho phân tích tỷ lệ lấp đầy
Table fact_ton_kho_vi_tri {
  snapshot_key uuid [pk]
  vi_tri_key uuid [ref: > dim_vi_tri_luu_tru.vi_tri_key]
  ngay_key date [ref: > dim_date.date_key]
  so_ho_so_hien_co integer
  ty_le_lap_day numeric(5,4)
}
', 'ACCEPTED', 'a678ac27-3077-5ef2-8919-5218b2e48791'::uuid, 'b276cfe5-c34e-56f4-b56d-7fd4ed51f1fc'::uuid, '2026-08-10 08:36:10+00:00', '2026-08-10 09:20:00+00:00', 'Table "dim_benh_nhan" {
  "benh_nhan_key" uuid [pk]
  "so_ho_so_hash" varchar(64) [note: ''SHA-256 của so_ho_so, dùng để truy vết'']
  "tuoi" integer
  "gioi_tinh" varchar(10)
  "nhom_tuoi" varchar(20)
  "doi_tuong_chi_tra" varchar(50)
  "nghe_nghiep" varchar(50)
}

Table "dim_khoa" {
  "khoa_key" varchar(10) [pk]
  "ten_khoa" varchar(100)
}

Table "dim_vi_tri_luu_tru" {
  "vi_tri_key" uuid [pk]
  "kho" varchar(50)
  "tu" varchar(50)
  "ngan" varchar(50)
  "suc_chua" integer
}

Table "dim_trang_thai_ho_so" {
  "trang_thai_key" varchar(10) [pk]
  "ten_trang_thai" varchar(50)
}

Table "dim_date" {
  "date_key" date [pk]
  "nam" integer
  "quy" integer
  "thang" "timestamp with time zone"
}

Table "dim_loai_benh_an" {
  "loai_key" varchar(10) [pk]
  "ten_loai" varchar(100)
}

Table "fact_ho_so_luu_tru" {
  "so_benh_an" varchar(30) [pk]
  "benh_nhan_key" uuid
  "khoa_vao_key" varchar(10)
  "khoa_ra_key" varchar(10)
  "vi_tri_key" uuid
  "trang_thai_key" varchar(10)
  "loai_key" varchar(10)
  "ngay_vao_key" date
  "ngay_ra_key" date
  "ngay_luu_tru_key" date
  "so_ngay_dieu_tri" integer
  "so_ngay_den_khi_luu_tru" integer
}

Ref:"dim_benh_nhan"."benh_nhan_key" < "fact_ho_so_luu_tru"."benh_nhan_key"

Ref:"dim_khoa"."khoa_key" < "fact_ho_so_luu_tru"."khoa_vao_key"

Ref:"dim_khoa"."khoa_key" < "fact_ho_so_luu_tru"."khoa_ra_key"

Ref:"dim_vi_tri_luu_tru"."vi_tri_key" < "fact_ho_so_luu_tru"."vi_tri_key"

Ref:"dim_trang_thai_ho_so"."trang_thai_key" < "fact_ho_so_luu_tru"."trang_thai_key"

Ref:"dim_loai_benh_an"."loai_key" < "fact_ho_so_luu_tru"."loai_key"

Ref:"dim_date"."date_key" < "fact_ho_so_luu_tru"."ngay_vao_key"

Ref:"dim_date"."date_key" < "fact_ho_so_luu_tru"."ngay_ra_key"

Ref:"dim_date"."date_key" < "fact_ho_so_luu_tru"."ngay_luu_tru_key"
'),
  ('334a17ab-5a72-55be-9df9-5fd337c22a6c'::uuid, 2, 'Table dim_benh_nhan {
  benh_nhan_key uuid [pk]
  so_ho_so_hash varchar(64) [note: ''SHA-256 của so_ho_so, dùng để truy vết'']
  tuoi integer
  gioi_tinh varchar(10)
  nhom_tuoi varchar(20)
  doi_tuong_chi_tra varchar(50)
  nghe_nghiep varchar(50)
  // đề xuất song song: thêm truong_thanh_toan
}

Table dim_khoa {
  khoa_key varchar(10) [pk]
  ten_khoa varchar(100)
}

Table dim_vi_tri_luu_tru {
  vi_tri_key uuid [pk]
  kho varchar(50)
  tu varchar(50)
  ngan varchar(50)
  suc_chua integer
}

Table dim_trang_thai_ho_so {
  trang_thai_key varchar(10) [pk]
  ten_trang_thai varchar(50)
}

Table dim_date {
  date_key date [pk]
  nam integer
  quy integer
  thang integer
}

Table dim_loai_benh_an {
  loai_key varchar(10) [pk]
  ten_loai varchar(100)
}

Table fact_ho_so_luu_tru {
  so_benh_an varchar(30) [pk]
  benh_nhan_key uuid [ref: > dim_benh_nhan.benh_nhan_key]
  khoa_vao_key varchar(10) [ref: > dim_khoa.khoa_key]
  khoa_ra_key varchar(10) [ref: > dim_khoa.khoa_key]
  vi_tri_key uuid [ref: > dim_vi_tri_luu_tru.vi_tri_key]
  trang_thai_key varchar(10) [ref: > dim_trang_thai_ho_so.trang_thai_key]
  loai_key varchar(10) [ref: > dim_loai_benh_an.loai_key]
  ngay_vao_key date [ref: > dim_date.date_key]
  ngay_ra_key date [ref: > dim_date.date_key]
  ngay_luu_tru_key date [ref: > dim_date.date_key]
  so_ngay_dieu_tri integer
  so_ngay_den_khi_luu_tru integer
}
', 'REJECTED', 'e892c55a-77c6-5c8f-8e00-00da20839ba9'::uuid, '8a59b785-2998-5116-81ab-90ae43f6667d'::uuid, '2025-11-05 02:00:00+00:00', '2025-11-05 03:15:00+00:00', 'Table "dim_benh_nhan" {
  "benh_nhan_key" uuid [pk]
  "so_ho_so_hash" varchar(64) [note: ''SHA-256 của so_ho_so, dùng để truy vết'']
  "tuoi" integer
  "gioi_tinh" varchar(10)
  "nhom_tuoi" varchar(20)
  "doi_tuong_chi_tra" varchar(50)
  "nghe_nghiep" varchar(50)
}

Table "dim_khoa" {
  "khoa_key" varchar(10) [pk]
  "ten_khoa" varchar(100)
}

Table "dim_vi_tri_luu_tru" {
  "vi_tri_key" uuid [pk]
  "kho" varchar(50)
  "tu" varchar(50)
  "ngan" varchar(50)
  "suc_chua" integer
}

Table "dim_trang_thai_ho_so" {
  "trang_thai_key" varchar(10) [pk]
  "ten_trang_thai" varchar(50)
}

Table "dim_date" {
  "date_key" date [pk]
  "nam" integer
  "quy" integer
  "thang" "timestamp with time zone"
}

Table "dim_loai_benh_an" {
  "loai_key" varchar(10) [pk]
  "ten_loai" varchar(100)
}

Table "fact_ho_so_luu_tru" {
  "so_benh_an" varchar(30) [pk]
  "benh_nhan_key" uuid
  "khoa_vao_key" varchar(10)
  "khoa_ra_key" varchar(10)
  "vi_tri_key" uuid
  "trang_thai_key" varchar(10)
  "loai_key" varchar(10)
  "ngay_vao_key" date
  "ngay_ra_key" date
  "ngay_luu_tru_key" date
  "so_ngay_dieu_tri" integer
  "so_ngay_den_khi_luu_tru" integer
}

Ref:"dim_benh_nhan"."benh_nhan_key" < "fact_ho_so_luu_tru"."benh_nhan_key"

Ref:"dim_khoa"."khoa_key" < "fact_ho_so_luu_tru"."khoa_vao_key"

Ref:"dim_khoa"."khoa_key" < "fact_ho_so_luu_tru"."khoa_ra_key"

Ref:"dim_vi_tri_luu_tru"."vi_tri_key" < "fact_ho_so_luu_tru"."vi_tri_key"

Ref:"dim_trang_thai_ho_so"."trang_thai_key" < "fact_ho_so_luu_tru"."trang_thai_key"

Ref:"dim_loai_benh_an"."loai_key" < "fact_ho_so_luu_tru"."loai_key"

Ref:"dim_date"."date_key" < "fact_ho_so_luu_tru"."ngay_vao_key"

Ref:"dim_date"."date_key" < "fact_ho_so_luu_tru"."ngay_ra_key"

Ref:"dim_date"."date_key" < "fact_ho_so_luu_tru"."ngay_luu_tru_key"
'),
  ('334a17ab-5a72-55be-9df9-5fd337c22a6c'::uuid, 3, 'Table dim_benh_nhan {
  benh_nhan_key uuid [pk]
  so_ho_so_hash varchar(64) [note: ''SHA-256 của so_ho_so, dùng để truy vết'']
  tuoi integer
  gioi_tinh varchar(10)
  nhom_tuoi varchar(20)
  doi_tuong_chi_tra varchar(50)
  nghe_nghiep varchar(50)
}

Table dim_khoa {
  khoa_key varchar(10) [pk]
  ten_khoa varchar(100)
}

Table dim_vi_tri_luu_tru {
  vi_tri_key uuid [pk]
  kho varchar(50)
  tu varchar(50)
  ngan varchar(50)
  suc_chua integer
}

Table dim_trang_thai_ho_so {
  trang_thai_key varchar(10) [pk]
  ten_trang_thai varchar(50)
}

Table dim_date {
  date_key date [pk]
  nam integer
  quy integer
  thang integer
}

Table dim_loai_benh_an {
  loai_key varchar(10) [pk]
  ten_loai varchar(100)
}

Table fact_ho_so_luu_tru {
  so_benh_an varchar(30) [pk]
  benh_nhan_key uuid [ref: > dim_benh_nhan.benh_nhan_key]
  khoa_vao_key varchar(10) [ref: > dim_khoa.khoa_key]
  khoa_ra_key varchar(10) [ref: > dim_khoa.khoa_key]
  vi_tri_key uuid [ref: > dim_vi_tri_luu_tru.vi_tri_key]
  trang_thai_key varchar(10) [ref: > dim_trang_thai_ho_so.trang_thai_key]
  loai_key varchar(10) [ref: > dim_loai_benh_an.loai_key]
  ngay_vao_key date [ref: > dim_date.date_key]
  ngay_ra_key date [ref: > dim_date.date_key]
  ngay_luu_tru_key date [ref: > dim_date.date_key]
  so_ngay_dieu_tri integer
  so_ngay_den_khi_luu_tru integer
}

// v4 (đang chờ duyệt): thêm dim_bac_si phục vụ phân tích theo bác sĩ phụ trách
Table dim_bac_si {
  bac_si_key uuid [pk]
  ten_bac_si_hash varchar(64)
  khoa_key varchar(10) [ref: > dim_khoa.khoa_key]
}
', 'PROPOSED', 'a678ac27-3077-5ef2-8919-5218b2e48791'::uuid, '15ceb42f-f3ad-5acd-a797-7fdb686272f0'::uuid, '2026-08-11 01:30:00+00:00', '2026-08-11 01:30:00+00:00', 'Table "dim_benh_nhan" {
  "benh_nhan_key" uuid [pk]
  "so_ho_so_hash" varchar(64) [note: ''SHA-256 của so_ho_so, dùng để truy vết'']
  "tuoi" integer
  "gioi_tinh" varchar(10)
  "nhom_tuoi" varchar(20)
  "doi_tuong_chi_tra" varchar(50)
  "nghe_nghiep" varchar(50)
}

Table "dim_khoa" {
  "khoa_key" varchar(10) [pk]
  "ten_khoa" varchar(100)
}

Table "dim_vi_tri_luu_tru" {
  "vi_tri_key" uuid [pk]
  "kho" varchar(50)
  "tu" varchar(50)
  "ngan" varchar(50)
  "suc_chua" integer
}

Table "dim_trang_thai_ho_so" {
  "trang_thai_key" varchar(10) [pk]
  "ten_trang_thai" varchar(50)
}

Table "dim_date" {
  "date_key" date [pk]
  "nam" integer
  "quy" integer
  "thang" "timestamp with time zone"
}

Table "dim_loai_benh_an" {
  "loai_key" varchar(10) [pk]
  "ten_loai" varchar(100)
}

Table "fact_ho_so_luu_tru" {
  "so_benh_an" varchar(30) [pk]
  "benh_nhan_key" uuid
  "khoa_vao_key" varchar(10)
  "khoa_ra_key" varchar(10)
  "vi_tri_key" uuid
  "trang_thai_key" varchar(10)
  "loai_key" varchar(10)
  "ngay_vao_key" date
  "ngay_ra_key" date
  "ngay_luu_tru_key" date
  "so_ngay_dieu_tri" integer
  "so_ngay_den_khi_luu_tru" integer
}

Ref:"dim_benh_nhan"."benh_nhan_key" < "fact_ho_so_luu_tru"."benh_nhan_key"

Ref:"dim_khoa"."khoa_key" < "fact_ho_so_luu_tru"."khoa_vao_key"

Ref:"dim_khoa"."khoa_key" < "fact_ho_so_luu_tru"."khoa_ra_key"

Ref:"dim_vi_tri_luu_tru"."vi_tri_key" < "fact_ho_so_luu_tru"."vi_tri_key"

Ref:"dim_trang_thai_ho_so"."trang_thai_key" < "fact_ho_so_luu_tru"."trang_thai_key"

Ref:"dim_loai_benh_an"."loai_key" < "fact_ho_so_luu_tru"."loai_key"

Ref:"dim_date"."date_key" < "fact_ho_so_luu_tru"."ngay_vao_key"

Ref:"dim_date"."date_key" < "fact_ho_so_luu_tru"."ngay_ra_key"

Ref:"dim_date"."date_key" < "fact_ho_so_luu_tru"."ngay_luu_tru_key"
'),
  ('f0cfe13c-7110-5ffe-bfc6-7bd37be7e8b8'::uuid, 1, 'Table dim_khoa {
  khoa_key varchar(10) [pk]
  ten_khoa varchar(100)
}

Table dim_chan_doan {
  chan_doan_key uuid [pk]
  ten_chan_doan varchar(250)
  nhom_chan_doan varchar(100)
}

Table dim_doi_tuong {
  doi_tuong_key varchar(20) [pk]
  ten_doi_tuong varchar(50)
}

Table dim_date {
  date_key date [pk]
  nam integer
  quy integer
  thang integer
}

Table fact_luot_kham {
  luot_kham_key uuid [pk]
  khoa_vao_key varchar(10) [ref: > dim_khoa.khoa_key]
  khoa_ra_key varchar(10) [ref: > dim_khoa.khoa_key]
  chan_doan_key uuid [ref: > dim_chan_doan.chan_doan_key]
  doi_tuong_key varchar(20) [ref: > dim_doi_tuong.doi_tuong_key]
  ngay_vao_key date [ref: > dim_date.date_key]
  so_luot integer
}

// đề xuất: thêm dim_bac_si_chan_doan
', 'PROPOSED', '4c507932-ae90-57a1-8765-885e45eba112'::uuid, 'e7131a5f-c437-5bea-917d-711990125d77'::uuid, '2025-12-11 02:00:00+00:00', '2025-12-11 02:00:00+00:00', 'Table dim_khoa {
  khoa_key varchar(10) [pk]
  ten_khoa varchar(100)
}

Table dim_chan_doan {
  chan_doan_key uuid [pk]
  ten_chan_doan varchar(250)
  nhom_chan_doan varchar(100)
}

Table dim_doi_tuong {
  doi_tuong_key varchar(20) [pk]
  ten_doi_tuong varchar(50)
}

Table dim_date {
  date_key date [pk]
  nam integer
  quy integer
  thang integer
}

Table fact_luot_kham {
  luot_kham_key uuid [pk]
  khoa_vao_key varchar(10) [ref: > dim_khoa.khoa_key]
  khoa_ra_key varchar(10) [ref: > dim_khoa.khoa_key]
  chan_doan_key uuid [ref: > dim_chan_doan.chan_doan_key]
  doi_tuong_key varchar(20) [ref: > dim_doi_tuong.doi_tuong_key]
  ngay_vao_key date [ref: > dim_date.date_key]
  so_luot integer
}
'),
  ('669b488c-5595-518f-a10b-2d02e1561333'::uuid, 1, 'Table dim_customer {
  customer_key bigint [pk]
  segment varchar(30)
  risk_score integer
  kyc_status varchar(20)
}

Table dim_account {
  account_key varchar(20) [pk]
  customer_key bigint [ref: > dim_customer.customer_key]
  account_type varchar(20)
}

Table dim_channel {
  channel_key varchar(20) [pk]
  channel_name varchar(50)
}

Table dim_date {
  date_key date [pk]
  nam integer
  thang integer
  ngay integer
}

Table fact_transaction {
  transaction_key bigint [pk]
  account_key varchar(20) [ref: > dim_account.account_key]
  channel_key varchar(20) [ref: > dim_channel.channel_key]
  date_key date [ref: > dim_date.date_key]
  amount numeric(18,2)
  is_flagged boolean
  fraud_score numeric(5,4) // v2: thêm điểm rủi ro gian lận
}
', 'ACCEPTED', '0740e12f-bc1c-556f-9cc7-3ec5332e692e'::uuid, '5c975d54-8385-5f7f-91d0-48ccf5806f67'::uuid, '2025-11-08 06:00:00+00:00', '2025-11-08 07:00:00+00:00', 'Table dim_customer {
  customer_key bigint [pk]
  segment varchar(30)
  risk_score integer
  kyc_status varchar(20)
}

Table dim_account {
  account_key varchar(20) [pk]
  customer_key bigint [ref: > dim_customer.customer_key]
  account_type varchar(20)
}

Table dim_channel {
  channel_key varchar(20) [pk]
  channel_name varchar(50)
}

Table dim_date {
  date_key date [pk]
  nam integer
  thang integer
  ngay integer
}

Table fact_transaction {
  transaction_key bigint [pk]
  account_key varchar(20) [ref: > dim_account.account_key]
  channel_key varchar(20) [ref: > dim_channel.channel_key]
  date_key date [ref: > dim_date.date_key]
  amount numeric(18,2)
  is_flagged boolean
}
'),
  ('669b488c-5595-518f-a10b-2d02e1561333'::uuid, 1, 'Table dim_customer {
  customer_key bigint [pk]
  segment varchar(30)
  risk_score integer
  credit_limit numeric(18,2) // đề xuất dựa trên revision cũ
  kyc_status varchar(20)
}

Table dim_account {
  account_key varchar(20) [pk]
  customer_key bigint [ref: > dim_customer.customer_key]
  account_type varchar(20)
}

Table dim_channel {
  channel_key varchar(20) [pk]
  channel_name varchar(50)
}

Table dim_date {
  date_key date [pk]
  nam integer
  thang integer
  ngay integer
}

Table fact_transaction {
  transaction_key bigint [pk]
  account_key varchar(20) [ref: > dim_account.account_key]
  channel_key varchar(20) [ref: > dim_channel.channel_key]
  date_key date [ref: > dim_date.date_key]
  amount numeric(18,2)
  is_flagged boolean
}
', 'CONFLICTED', '187ebbb4-aff9-555e-93e8-84718180c565'::uuid, '1ccf808f-beaf-5193-91b6-6a216432b7ca'::uuid, '2025-11-08 06:10:00+00:00', '2025-11-08 07:05:00+00:00', 'Table dim_customer {
  customer_key bigint [pk]
  segment varchar(30)
  risk_score integer
  kyc_status varchar(20)
}

Table dim_account {
  account_key varchar(20) [pk]
  customer_key bigint [ref: > dim_customer.customer_key]
  account_type varchar(20)
}

Table dim_channel {
  channel_key varchar(20) [pk]
  channel_name varchar(50)
}

Table dim_date {
  date_key date [pk]
  nam integer
  thang integer
  ngay integer
}

Table fact_transaction {
  transaction_key bigint [pk]
  account_key varchar(20) [ref: > dim_account.account_key]
  channel_key varchar(20) [ref: > dim_channel.channel_key]
  date_key date [ref: > dim_date.date_key]
  amount numeric(18,2)
  is_flagged boolean
}
'),
  ('a42297a7-08d0-592a-b70a-8409a153ff05'::uuid, 1, 'Table dim_sku {
  sku_key varchar(30) [pk]
  category varchar(50)
  brand varchar(50)
}

Table dim_store {
  store_key varchar(10) [pk]
  region varchar(50)
  store_type varchar(30)
}

Table dim_date {
  date_key date [pk]
  nam integer
  tuan integer
}

Table fact_doanh_thu_ban_hang {
  invoice_line_key uuid [pk]
  sku_key varchar(30) [ref: > dim_sku.sku_key]
  store_key varchar(10) [ref: > dim_store.store_key]
  date_key date [ref: > dim_date.date_key]
  qty integer
  revenue numeric(14,2)
  discount_amount numeric(14,2)
  promo_code varchar(20) // đề xuất bổ sung mã khuyến mãi
}
', 'REJECTED', '25a6f954-f1cd-567d-88a0-630c4407b254'::uuid, '91e373e7-f5a4-519a-8743-c6c10e9c6c65'::uuid, '2025-11-12 02:00:00+00:00', '2025-11-12 03:30:00+00:00', 'Table dim_sku {
  sku_key varchar(30) [pk]
  category varchar(50)
  brand varchar(50)
}

Table dim_store {
  store_key varchar(10) [pk]
  region varchar(50)
  store_type varchar(30)
}

Table dim_date {
  date_key date [pk]
  nam integer
  tuan integer
}

Table fact_doanh_thu_ban_hang {
  invoice_line_key uuid [pk]
  sku_key varchar(30) [ref: > dim_sku.sku_key]
  store_key varchar(10) [ref: > dim_store.store_key]
  date_key date [ref: > dim_date.date_key]
  qty integer
  revenue numeric(14,2)
  discount_amount numeric(14,2)
}
'),
  ('26d054de-06b0-51ca-86d3-270a75cc88f3'::uuid, 1, 'Table dim_route {
  route_key varchar(20) [pk]
  origin_hub varchar(50)
  dest_hub varchar(50)
}

Table dim_carrier {
  carrier_key varchar(20) [pk]
  carrier_name varchar(100)
  vehicle_type varchar(30)
}

Table dim_date {
  date_key date [pk]
  nam integer
  thang integer
}

Table fact_shipment {
  shipment_key varchar(30) [pk]
  route_key varchar(20) [ref: > dim_route.route_key]
  carrier_key varchar(20) [ref: > dim_carrier.carrier_key]
  date_key date [ref: > dim_date.date_key]
  sla_hours integer
  actual_hours numeric(6,2)
  is_on_time boolean
  delay_minutes integer // v2: thêm số phút trễ
}
', 'ACCEPTED', '85651d6b-4cc0-56ba-ba15-ffc404f10abc'::uuid, 'f649588b-edb9-52ed-8fc1-f3fc8be59bb4'::uuid, '2025-11-19 01:00:00+00:00', '2025-11-20 02:00:00+00:00', 'Table dim_route {
  route_key varchar(20) [pk]
  origin_hub varchar(50)
  dest_hub varchar(50)
}

Table dim_carrier {
  carrier_key varchar(20) [pk]
  carrier_name varchar(100)
  vehicle_type varchar(30)
}

Table dim_date {
  date_key date [pk]
  nam integer
  thang integer
}

Table fact_shipment {
  shipment_key varchar(30) [pk]
  route_key varchar(20) [ref: > dim_route.route_key]
  carrier_key varchar(20) [ref: > dim_carrier.carrier_key]
  date_key date [ref: > dim_date.date_key]
  sla_hours integer
  actual_hours numeric(6,2)
  is_on_time boolean
}
'),
  ('353a2d9e-ab98-5c99-b541-5a168aa5b332'::uuid, 1, 'Table dim_line {
  line_key varchar(10) [pk]
  line_name varchar(50)
}

Table dim_shift {
  shift_key varchar(5) [pk]
  shift_name varchar(30)
}

Table fact_production {
  event_key bigint [pk]
  line_key varchar(10) [ref: > dim_line.line_key]
  shift_key varchar(5) [ref: > dim_shift.shift_key]
  planned_units integer
  produced_units integer
  defect_units integer
  downtime_minutes integer
  availability numeric(5,4)
  performance numeric(5,4)
  quality numeric(5,4)
  oee numeric(5,4)
  target_oee numeric(5,4) // đề xuất thêm mục tiêu OEE để so sánh
}
', 'PROPOSED', 'c0445430-562e-5472-bea6-06f3a5d6f645'::uuid, 'd7b57f42-cbef-55b3-a758-18d52334387e'::uuid, '2025-12-09 02:00:00+00:00', '2025-12-09 02:00:00+00:00', 'Table dim_line {
  line_key varchar(10) [pk]
  line_name varchar(50)
}

Table dim_shift {
  shift_key varchar(5) [pk]
  shift_name varchar(30)
}

Table fact_production {
  event_key bigint [pk]
  line_key varchar(10) [ref: > dim_line.line_key]
  shift_key varchar(5) [ref: > dim_shift.shift_key]
  planned_units integer
  produced_units integer
  defect_units integer
  downtime_minutes integer
  availability numeric(5,4)
  performance numeric(5,4)
  quality numeric(5,4)
  oee numeric(5,4)
}
'),
  ('c68e1dd1-f2d4-50bd-bd34-9743e6d79968'::uuid, 1, 'Table dim_subscriber {
  subscriber_key varchar(15) [pk]
  plan_key varchar(10)
  region varchar(30)
  status varchar(15)
}

Table dim_plan {
  plan_key varchar(10) [pk]
  plan_name varchar(50)
}

Table dim_date {
  date_key date [pk]
  nam integer
  thang integer
}

Table fact_usage_monthly {
  usage_key uuid [pk]
  subscriber_key varchar(15) [ref: > dim_subscriber.subscriber_key]
  date_key date [ref: > dim_date.date_key]
  total_data_mb numeric(14,2)
  total_voice_minutes numeric(12,2)
  arpu numeric(12,2)
  is_churned boolean
  churn_risk_score numeric(5,4) // v2: bổ sung điểm dự báo rời mạng
}
', 'ACCEPTED', 'e892c55a-77c6-5c8f-8e00-00da20839ba9'::uuid, '685f57f6-e920-5c1d-bcd0-abfb9653882d'::uuid, '2025-12-16 01:00:00+00:00', '2025-12-18 02:00:00+00:00', 'Table dim_subscriber {
  subscriber_key varchar(15) [pk]
  plan_key varchar(10)
  region varchar(30)
  status varchar(15)
}

Table dim_plan {
  plan_key varchar(10) [pk]
  plan_name varchar(50)
}

Table dim_date {
  date_key date [pk]
  nam integer
  thang integer
}

Table fact_usage_monthly {
  usage_key uuid [pk]
  subscriber_key varchar(15) [ref: > dim_subscriber.subscriber_key]
  date_key date [ref: > dim_date.date_key]
  total_data_mb numeric(14,2)
  total_voice_minutes numeric(12,2)
  arpu numeric(12,2)
  is_churned boolean
}
'),
  ('97998605-51ac-53da-8391-89e07a426729'::uuid, 1, 'Table dim_category {
  category_key varchar(30) [pk]
  category_name varchar(100)
}

Table dim_channel {
  channel_key varchar(20) [pk]
  channel_name varchar(50)
}

Table fact_cart_funnel {
  event_key uuid [pk]
  category_key varchar(30) [ref: > dim_category.category_key]
  channel_key varchar(20) [ref: > dim_channel.channel_key]
  add_to_cart_count integer
  checkout_count integer
  purchase_count integer
}

Table fact_ad_spend {
  campaign_key varchar(20) [pk]
  channel_key varchar(20) [ref: > dim_channel.channel_key]
  spend numeric(14,2)
  conversions integer
}

// đề xuất: thêm fact_customer_ltv
', 'PROPOSED', '4c507932-ae90-57a1-8765-885e45eba112'::uuid, '8a1746e4-8593-5ec7-b20c-4fa94ceb1032'::uuid, '2026-01-06 04:00:00+00:00', '2026-01-06 04:00:00+00:00', 'Table dim_category {
  category_key varchar(30) [pk]
  category_name varchar(100)
}

Table dim_channel {
  channel_key varchar(20) [pk]
  channel_name varchar(50)
}

Table fact_cart_funnel {
  event_key uuid [pk]
  category_key varchar(30) [ref: > dim_category.category_key]
  channel_key varchar(20) [ref: > dim_channel.channel_key]
  add_to_cart_count integer
  checkout_count integer
  purchase_count integer
}

Table fact_ad_spend {
  campaign_key varchar(20) [pk]
  channel_key varchar(20) [ref: > dim_channel.channel_key]
  spend numeric(14,2)
  conversions integer
}
'),
  ('11ec29ff-332c-4dbe-824c-f9390fb8e8cb'::uuid, 1, 'Table Dim_BenhNhan {
  BenhNhan_Key integer [pk, increment]
  SoHoSo varchar(50) [not null]
  HoTen varchar(255)
  GioiTinh varchar(20)
  DiaChi varchar(255)
  NgheNghiep varchar(100)
  DoiTuong varchar(100)
  LoaiDieuTri varchar(100)
}

Table Dim_KhoaPhong {
  Khoa_Key integer [pk, increment]
  TenKhoa varchar(255) [not null]
}

Table Dim_ChanDoan {
  ChanDoan_Key integer [pk, increment]
  TenChanDoan varchar(255) [not null]
}

Table Dim_ViTriLuuTru {
  ViTri_Key integer [pk, increment]
  Kho varchar(100)
  Tu varchar(100)
  Ngan varchar(100)
  ViTriChiTiet varchar(100)
}

Table Dim_TrangThaiHoSo {
  TrangThai_Key integer [pk, increment]
  TenTrangThai varchar(100) [not null]
}

Table Dim_Date {
  Date_Key integer [pk]
  FullDate date [not null]
  Day integer
  Month integer
  Quarter integer
  Year integer
}

Table Fact_DieuTri {
  Fact_DieuTri_Key bigint [pk, increment]
  BenhNhan_Key integer [not null]
  KhoaVao_Key integer [not null]
  KhoaRa_Key integer [not null]
  ChanDoan_Key integer [not null]
  NgayVao_Key integer [not null]
  NgayRa_Key integer [not null]
  Tuoi integer
  ThoiGianVaoVien datetime
  NgayRaVien datetime
  SoNgayDieuTri numeric(10,2)
}

Table Fact_LuuTruHoSo {
  Fact_LuuTru_Key bigint [pk, increment]
  BenhNhan_Key integer [not null]
  KhoaVao_Key integer [not null]
  KhoaRa_Key integer [not null]
  ChanDoan_Key integer [not null]
  ViTri_Key integer [not null]
  TrangThai_Key integer [not null]
  NgayVao_Key integer [not null]
  NgayRa_Key integer [not null]
  NgayLuuTru_Key integer [not null]
  SoBenhAn varchar(50)
  SoLuuTru integer
  KyHieu varchar(100)
  GhiChu text
  SoLuongHoSo integer
}

Ref: Fact_DieuTri.BenhNhan_Key > Dim_BenhNhan.BenhNhan_Key
Ref: Fact_DieuTri.KhoaVao_Key > Dim_KhoaPhong.Khoa_Key
Ref: Fact_DieuTri.KhoaRa_Key > Dim_KhoaPhong.Khoa_Key
Ref: Fact_DieuTri.ChanDoan_Key > Dim_ChanDoan.ChanDoan_Key
Ref: Fact_DieuTri.NgayVao_Key > Dim_Date.Date_Key
Ref: Fact_DieuTri.NgayRa_Key > Dim_Date.Date_Key
Ref: Fact_LuuTruHoSo.BenhNhan_Key > Dim_BenhNhan.BenhNhan_Key
Ref: Fact_LuuTruHoSo.KhoaVao_Key > Dim_KhoaPhong.Khoa_Key
Ref: Fact_LuuTruHoSo.KhoaRa_Key > Dim_KhoaPhong.Khoa_Key
Ref: Fact_LuuTruHoSo.ChanDoan_Key > Dim_ChanDoan.ChanDoan_Key
Ref: Fact_LuuTruHoSo.ViTri_Key > Dim_ViTriLuuTru.ViTri_Key
Ref: Fact_LuuTruHoSo.TrangThai_Key > Dim_TrangThaiHoSo.TrangThai_Key
Ref: Fact_LuuTruHoSo.NgayVao_Key > Dim_Date.Date_Key
Ref: Fact_LuuTruHoSo.NgayRa_Key > Dim_Date.Date_Key
Ref: Fact_LuuTruHoSo.NgayLuuTru_Key > Dim_Date.Date_Key', 'REJECTED', 'a678ac27-3077-5ef2-8919-5218b2e48791'::uuid, 'f8f4f428-f0bc-4057-8eb0-9cf8052959cb'::uuid, '2026-08-22 16:25:03.653904+00:00', '2026-08-22 16:44:56.664839+00:00', 'Table "Dim_BenhNhan" {
  "BenhNhan_Key" integer [pk, increment]
  "SoHoSo" varchar(50) [not null]
  "HoTen" varchar(255)
  "GioiTinh" varchar(20)
  "DiaChi" varchar(255)
  "NgheNghiep" varchar(100)
  "DoiTuong" varchar(100)
  "LoaiDieuTri" varchar(100)
}

Table "Dim_KhoaPhong" {
  "Khoa_Key" integer [pk, increment]
  "TenKhoa" varchar(255) [not null]
}

Table "Dim_ChanDoan" {
  "ChanDoan_Key" integer [pk, increment]
  "TenChanDoan" varchar(255) [not null]
}

Table "Dim_ViTriLuuTru" {
  "ViTri_Key" integer [pk, increment]
  "Kho" varchar(100)
  "Tu" varchar(100)
  "Ngan" varchar(100)
  "ViTriChiTiet" varchar(100)
}

Table "Dim_TrangThaiHoSo" {
  "TrangThai_Key" integer [pk, increment]
  "TenTrangThai" varchar(100) [not null]
}

Table "Dim_Date" {
  "Date_Key" integer [pk]
  "FullDate" date [not null]
  "Day" integer
  "Month" integer
  "Quarter" integer
  "Year" integer
}

Table "Fact_DieuTri" {
  "Fact_DieuTri_Key" bigint [pk, increment]
  "BenhNhan_Key" integer [not null]
  "KhoaVao_Key" integer [not null]
  "KhoaRa_Key" integer [not null]
  "ChanDoan_Key" integer [not null]
  "NgayVao_Key" integer [not null]
  "NgayRa_Key" integer [not null]
  "Tuoi" integer
  "ThoiGianVaoVien" datetime
  "NgayRaVien" datetime
  "SoNgayDieuTri" numeric(10,2)
}

Table "Fact_LuuTruHoSo" {
  "Fact_LuuTru_Key" bigint [pk, increment]
  "BenhNhan_Key" integer [not null]
  "ViTri_Key" integer [not null]
  "TrangThai_Key" integer [not null]
  "ChanDoan_Key" integer [not null]
  "NgayLuuTru_Key" integer [not null]
  "SoBenhAn" varchar(50)
  "SoLuuTru" integer
  "KyHieu" varchar(100)
  "GhiChu" text
  "SoLuongHoSo" integer
}
'),
  ('11ec29ff-332c-4dbe-824c-f9390fb8e8cb'::uuid, 3, 'Table "Dim_BenhNhan" {
  "BenhNhan_Key" integer [pk, increment]
  "SoHoSo" varchar(50) [not null]
  "HoTen" varchar(255)
  "GioiTinh" varchar(20)
  "DiaChi" varchar(255)
  "NgheNghiep" varchar(100)
  "DoiTuong" varchar(100)
  "LoaiDieuTri" varchar(100)
}

Table "Dim_KhoaPhong" {
  "Khoa_Key" integer [pk, increment]
  "TenKhoa" varchar(255) [not null]
}

Table "Dim_ChanDoan" {
  "ChanDoan_Key" integer [pk, increment]
  "TenChanDoan" varchar(255) [not null]
}

Table "Dim_ViTriLuuTru" {
  "ViTri_Key" integer [pk, increment]
  "Kho" varchar(100)
  "Tu" varchar(100)
  "Ngan" varchar(100)
  "ViTriChiTiet" varchar(100)
}

Table "Dim_TrangThaiHoSo" {
  "TrangThai_Key" integer [pk, increment]
  "TenTrangThai" varchar(100) [not null]
}

Table "Dim_Date" {
  "Date_Key" integer [pk]
  "FullDate" date [not null]
  "Day" integer
  "Month" integer
  "Quarter" integer
  "Year" integer
}

Table "Fact_DieuTri" {
  "Fact_DieuTri_Key" bigint [pk, increment]
  "BenhNhan_Key" integer [not null]
  "KhoaVao_Key" integer [not null]
  "KhoaRa_Key" integer [not null]
  "ChanDoan_Key" integer [not null]
  "NgayVao_Key" integer [not null]
  "NgayRa_Key" integer [not null]
  "Tuoi" integer
  "ThoiGianVaoVien" datetime
  "NgayRaVien" datetime
  "SoNgayDieuTri" numeric(10,2)
}

Table "Fact_LuuTruHoSo" {
  "Fact_LuuTru_Key" bigint [pk, increment]
  "BenhNhan_Key" integer [not null]
  "ViTri_Key" integer [not null]
  "TrangThai_Key" integer [not null]
  "ChanDoan_Key" integer [not null]
  "NgayLuuTru_Key" integer [not null]
  "SoBenhAn" varchar(50)
  "SoLuuTru" integer
  "KyHieu" varchar(100)
  "GhiChu" text
  "SoLuongHoSo" integer
}

Ref: "Fact_DieuTri"."BenhNhan_Key" > "Dim_BenhNhan"."BenhNhan_Key"
Ref: "Fact_DieuTri"."KhoaVao_Key" > "Dim_KhoaPhong"."Khoa_Key"
Ref: "Fact_DieuTri"."KhoaRa_Key" > "Dim_KhoaPhong"."Khoa_Key"
Ref: "Fact_DieuTri"."ChanDoan_Key" > "Dim_ChanDoan"."ChanDoan_Key"
Ref: "Fact_DieuTri"."NgayVao_Key" > "Dim_Date"."Date_Key"
Ref: "Fact_DieuTri"."NgayRa_Key" > "Dim_Date"."Date_Key"

Ref: "Fact_LuuTruHoSo"."BenhNhan_Key" > "Dim_BenhNhan"."BenhNhan_Key"
Ref: "Fact_LuuTruHoSo"."ViTri_Key" > "Dim_ViTriLuuTru"."ViTri_Key"
Ref: "Fact_LuuTruHoSo"."TrangThai_Key" > "Dim_TrangThaiHoSo"."TrangThai_Key"
Ref: "Fact_LuuTruHoSo"."ChanDoan_Key" > "Dim_ChanDoan"."ChanDoan_Key"
Ref: "Fact_LuuTruHoSo"."NgayLuuTru_Key" > "Dim_Date"."Date_Key"', 'ACCEPTED', 'a678ac27-3077-5ef2-8919-5218b2e48791'::uuid, 'c5069575-fb9c-4e2d-b09c-3350c449effe'::uuid, '2026-08-22 18:28:56.734407+00:00', '2026-08-22 18:50:44.006770+00:00', 'Table "Dim_BenhNhan" {
  "BenhNhan_Key" integer [pk, increment]
  "SoHoSo" varchar(50) [not null]
  "HoTen" varchar(255)
  "GioiTinh" varchar(20)
  "DiaChi" varchar(255)
  "NgheNghiep" varchar(100)
  "DoiTuong" varchar(100)
  "LoaiDieuTri" varchar(100)
}

Table "Dim_KhoaPhong" {
  "Khoa_Key" integer [pk, increment]
  "TenKhoa" varchar(255) [not null]
}

Table "Dim_ChanDoan" {
  "ChanDoan_Key" integer [pk, increment]
  "TenChanDoan" varchar(255) [not null]
}

Table "Dim_ViTriLuuTru" {
  "ViTri_Key" integer [pk, increment]
  "Kho" varchar(100)
  "Tu" varchar(100)
  "Ngan" varchar(100)
  "ViTriChiTiet" varchar(100)
}

Table "Dim_TrangThaiHoSo" {
  "TrangThai_Key" integer [pk, increment]
  "TenTrangThai" varchar(100) [not null]
}

Table "Dim_Date" {
  "Date_Key" integer [pk]
  "FullDate" date [not null]
  "Day" integer
  "Month" integer
  "Quarter" integer
  "Year" integer
}

Table "Fact_DieuTri" {
  "Fact_DieuTri_Key" bigint [pk, increment]
  "BenhNhan_Key" integer [not null]
  "KhoaVao_Key" integer [not null]
  "KhoaRa_Key" integer [not null]
  "ChanDoan_Key" integer [not null]
  "NgayVao_Key" integer [not null]
  "NgayRa_Key" integer [not null]
  "Tuoi" integer
  "ThoiGianVaoVien" datetime
  "NgayRaVien" datetime
  "SoNgayDieuTri" numeric(10,2)
}

Table "Fact_LuuTruHoSo" {
  "Fact_LuuTru_Key" bigint [pk, increment]
  "BenhNhan_Key" integer [not null]
  "ViTri_Key" integer [not null]
  "TrangThai_Key" integer [not null]
  "ChanDoan_Key" integer [not null]
  "NgayLuuTru_Key" integer [not null]
  "SoBenhAn" varchar(50)
  "SoLuuTru" integer
  "KyHieu" varchar(100)
  "GhiChu" text
  "SoLuongHoSo" integer
}
'),
  ('d7474a47-743b-4351-9bd9-a35e9933ca3c'::uuid, 4, 'Table "Dim_Date" {
  "date_key" integer [pk]
  "full_date" date
  "day" integer
  "month" integer
  "quarter" integer
  "year" integer
}

Table "Dim_BenhNhan" {
  "patient_key" integer [pk]
  "so_ho_so" varchar
  "so_benh_an" varchar
  "tuoi" integer
  "gioi_tinh" varchar
  "nghe_nghiep" varchar
  "doi_tuong_chi_tra" varchar
  "loai_dieu_tri" varchar
}

Table "Dim_Khoa" {
  "khoa_key" integer [pk]
  "ten_khoa" varchar
}

Table "Dim_ChanDoan" {
  "chan_doan_key" integer [pk]
  "ten_chan_doan" varchar
}

Table "Dim_ViTriLuuTru" {
  "vi_tri_key" integer [pk]
  "kho" varchar
  "tu" varchar
  "ngan" varchar
  "vi_tri_ke" varchar
  "ky_hieu" varchar
}

Table "Dim_TrangThaiHoSo" {
  "trang_thai_key" integer [pk]
  "ten_trang_thai" varchar
}

Table "Fact_KhamChuaBenh" {
  "kham_chua_benh_key" integer [pk]
  "patient_key" integer
  "vao_khoa_key" integer
  "ra_khoa_key" integer
  "chan_doan_key" integer
  "ngay_vao_key" integer
  "ngay_ra_key" integer
  "thoi_gian_dieu_tri_ngay" integer
  "so_luong_luot_kham" integer
}

Table "Fact_HoSoLuuTru" {
  "ho_so_luu_tru_key" integer [pk]
  "patient_key" integer
  "vi_tri_key" integer
  "trang_thai_key" integer
  "ngay_luu_tru_key" integer
  "so_luu_tru" integer
  "ghi_chu" varchar
  "so_luong_ho_so" integer
}

Ref: "Fact_KhamChuaBenh"."patient_key" > "Dim_BenhNhan"."patient_key"
Ref: "Fact_KhamChuaBenh"."vao_khoa_key" > "Dim_Khoa"."khoa_key"
Ref: "Fact_KhamChuaBenh"."ra_khoa_key" > "Dim_Khoa"."khoa_key"
Ref: "Fact_KhamChuaBenh"."chan_doan_key" > "Dim_ChanDoan"."chan_doan_key"
Ref: "Fact_KhamChuaBenh"."ngay_vao_key" > "Dim_Date"."date_key"
Ref: "Fact_KhamChuaBenh"."ngay_ra_key" > "Dim_Date"."date_key"
Ref: "Fact_HoSoLuuTru"."patient_key" > "Dim_BenhNhan"."patient_key"
Ref: "Fact_HoSoLuuTru"."vi_tri_key" > "Dim_ViTriLuuTru"."vi_tri_key"
Ref: "Fact_HoSoLuuTru"."trang_thai_key" > "Dim_TrangThaiHoSo"."trang_thai_key"
Ref: "Fact_HoSoLuuTru"."ngay_luu_tru_key" > "Dim_Date"."date_key"', 'ACCEPTED', '01b19ecb-53ef-4373-99a5-3b0d8bd3af61'::uuid, 'a214af38-c5a2-49e3-9148-46fa2dea28f0'::uuid, '2026-08-23 12:43:22.525554+00:00', '2026-08-23 12:44:24.614735+00:00', 'Table "Dim_Date" {
  "date_key" integer [pk]
  "full_date" date
  "day" integer
  "month" integer
  "quarter" integer
  "year" integer
}

Table "Dim_BenhNhan" {
  "patient_key" integer [pk]
  "so_ho_so" varchar
  "so_benh_an" varchar
  "tuoi" integer
  "gioi_tinh" varchar
  "nghe_nghiep" varchar
  "doi_tuong_chi_tra" varchar
  "loai_dieu_tri" varchar
}

Table "Dim_Khoa" {
  "khoa_key" integer [pk]
  "ten_khoa" varchar
}

Table "Dim_ChanDoan" {
  "chan_doan_key" integer [pk]
  "ten_chan_doan" varchar
}

Table "Dim_ViTriLuuTru" {
  "vi_tri_key" integer [pk]
  "kho" varchar
  "tu" varchar
  "ngan" varchar
  "vi_tri_ke" varchar
  "ky_hieu" varchar
}

Table "Dim_TrangThaiHoSo" {
  "trang_thai_key" integer [pk]
  "ten_trang_thai" varchar
}

Table "Fact_KhamChuaBenh" {
  "kham_chua_benh_key" integer [pk]
  "patient_key" integer
  "vao_khoa_key" integer
  "ra_khoa_key" integer
  "chan_doan_key" integer
  "ngay_vao_key" integer
  "ngay_ra_key" integer
  "thoi_gian_dieu_tri_ngay" integer
  "so_luong_luot_kham" integer
}

Table "Fact_HoSoLuuTru" {
  "ho_so_luu_tru_key" integer [pk]
  "patient_key" integer
  "vi_tri_key" integer
  "trang_thai_key" integer
  "ngay_luu_tru_key" integer
  "so_luu_tru" integer
  "ghi_chu" varchar
  "so_luong_ho_so" integer
}
'),
  ('d7474a47-743b-4351-9bd9-a35e9933ca3c'::uuid, 5, 'Table "Dim_Date" {
  "date_key" integer [pk]
  "full_date" date
  "day" integer
  "month" integer
  "quarter" integer
  "year" integer
}

Table "Dim_BenhNhan" {
  "patient_key" integer [pk]
  "so_ho_so" varchar
  "so_benh_an" varchar
  "tuoi" integer
  "gioi_tinh" varchar
  "nghe_nghiep" varchar
  "doi_tuong_chi_tra" varchar
  "loai_dieu_tri" varchar
}

Table "Dim_Khoa" {
  "khoa_key" integer [pk]
  "ten_khoa" varchar
}

Table "Dim_ChanDoan" {
  "chan_doan_key" integer [pk]
  "ten_chan_doan" varchar
}

Table "Dim_ViTriLuuTru" {
  "vi_tri_key" integer [pk]
  "kho" varchar
  "tu" varchar
  "ngan" varchar
  "vi_tri_ke" varchar
  "ky_hieu" varchar
}

Table "Dim_TrangThaiHoSo" {
  "trang_thai_key" integer [pk]
  "ten_trang_thai" varchar
}

Table "Fact_KhamChuaBenh" {
  "kham_chua_benh_key" integer [pk]
  "patient_key" integer
  "vao_khoa_key" integer
  "ra_khoa_key" integer
  "chan_doan_key" integer
  "ngay_vao_key" integer
  "ngay_ra_key" integer
  "thoi_gian_dieu_tri_ngay" integer
  "so_luong_luot_kham" integer
}

Table "Fact_HoSoLuuTru" {
  "ho_so_luu_tru_key" integer [pk]
  "patient_key" integer
  "vi_tri_key" integer
  "trang_thai_key" integer
  "ngay_luu_tru_key" integer
  "so_luu_tru" integer
  "ghi_chu" varchar
  "so_luong_ho_so" integer
}

Ref: "Fact_KhamChuaBenh"."patient_key" > "Dim_BenhNhan"."patient_key"
Ref: "Fact_KhamChuaBenh"."vao_khoa_key" > "Dim_Khoa"."khoa_key"
Ref: "Fact_KhamChuaBenh"."ra_khoa_key" > "Dim_Khoa"."khoa_key"
Ref: "Fact_KhamChuaBenh"."chan_doan_key" > "Dim_ChanDoan"."chan_doan_key"
Ref: "Fact_KhamChuaBenh"."ngay_vao_key" > "Dim_Date"."date_key"
Ref: "Fact_KhamChuaBenh"."ngay_ra_key" > "Dim_Date"."date_key"
Ref: "Fact_HoSoLuuTru"."patient_key" > "Dim_BenhNhan"."patient_key"
Ref: "Fact_HoSoLuuTru"."vi_tri_key" > "Dim_ViTriLuuTru"."vi_tri_key"
Ref: "Fact_HoSoLuuTru"."trang_thai_key" > "Dim_TrangThaiHoSo"."trang_thai_key"
Ref: "Fact_HoSoLuuTru"."ngay_luu_tru_key" > "Dim_Date"."date_key"', 'REJECTED', '01b19ecb-53ef-4373-99a5-3b0d8bd3af61'::uuid, '83b8c13e-76ee-4c35-b130-fd492a5fc23f'::uuid, '2026-08-24 08:18:18.139064+00:00', '2026-08-24 08:18:46.111064+00:00', 'Table "Dim_Date" {
  "date_key" integer [pk]
  "full_date" date
  "day" integer
  "month" integer
  "quarter" integer
  "year" integer
}

Table "Dim_BenhNhan" {
  "patient_key" integer [pk]
  "so_ho_so" varchar
  "so_benh_an" varchar
  "tuoi" integer
  "gioi_tinh" varchar
  "nghe_nghiep" varchar
  "doi_tuong_chi_tra" varchar
  "loai_dieu_tri" varchar
}

Table "Dim_Khoa" {
  "khoa_key" integer [pk]
  "ten_khoa" varchar
}

Table "Dim_ChanDoan" {
  "chan_doan_key" integer [pk]
  "ten_chan_doan" varchar
}

Table "Dim_ViTriLuuTru" {
  "vi_tri_key" integer [pk]
  "kho" varchar
  "tu" varchar
  "ngan" varchar
  "vi_tri_ke" varchar
  "ky_hieu" varchar
}

Table "Dim_TrangThaiHoSo" {
  "trang_thai_key" integer [pk]
  "ten_trang_thai" varchar
}

Table "Fact_KhamChuaBenh" {
  "kham_chua_benh_key" integer [pk]
  "patient_key" integer
  "vao_khoa_key" integer
  "ra_khoa_key" integer
  "chan_doan_key" integer
  "ngay_vao_key" integer
  "ngay_ra_key" integer
  "thoi_gian_dieu_tri_ngay" integer
  "so_luong_luot_kham" integer
}

Table "Fact_HoSoLuuTru" {
  "ho_so_luu_tru_key" integer [pk]
  "patient_key" integer
  "vi_tri_key" integer
  "trang_thai_key" integer
  "ngay_luu_tru_key" integer
  "so_luu_tru" integer
  "ghi_chu" varchar
  "so_luong_ho_so" integer
}

Ref: "Fact_KhamChuaBenh"."patient_key" > "Dim_BenhNhan"."patient_key"
Ref: "Fact_KhamChuaBenh"."vao_khoa_key" > "Dim_Khoa"."khoa_key"
Ref: "Fact_KhamChuaBenh"."ra_khoa_key" > "Dim_Khoa"."khoa_key"
Ref: "Fact_KhamChuaBenh"."chan_doan_key" > "Dim_ChanDoan"."chan_doan_key"
Ref: "Fact_KhamChuaBenh"."ngay_vao_key" > "Dim_Date"."date_key"
Ref: "Fact_KhamChuaBenh"."ngay_ra_key" > "Dim_Date"."date_key"
Ref: "Fact_HoSoLuuTru"."patient_key" > "Dim_BenhNhan"."patient_key"
Ref: "Fact_HoSoLuuTru"."vi_tri_key" > "Dim_ViTriLuuTru"."vi_tri_key"
Ref: "Fact_HoSoLuuTru"."trang_thai_key" > "Dim_TrangThaiHoSo"."trang_thai_key"
Ref: "Fact_HoSoLuuTru"."ngay_luu_tru_key" > "Dim_Date"."date_key"')
ON CONFLICT DO NOTHING;

-- Data for: project_sessions (18 rows)
INSERT INTO "project_sessions" ("project_id", "user_id", "title", "status", "id", "created_at", "updated_at", "active_turn_id", "active_turn_started_at", "pending_question_id", "conversation_summary", "summarized_through_event_id", "summary_updated_at", "purpose", "base_requirement_revision") VALUES
  ('7e621a51-f48a-53bf-927d-f415ae6c9249'::uuid, 'a678ac27-3077-5ef2-8919-5218b2e48791'::uuid, 'Thiết kế Data Warehouse Hồ sơ lưu trữ v1', 'COMPLETED', '9573f767-f342-56c0-90bc-c88ff63ee157'::uuid, '2025-11-04 02:30:00+00:00', '2025-11-04 04:45:00+00:00', NULL, NULL, NULL, NULL, NULL, NULL, 'DATA_MODELING', NULL),
  ('7e621a51-f48a-53bf-927d-f415ae6c9249'::uuid, '15c1be82-ea36-5205-af17-7fb5947c2027'::uuid, 'Điều chỉnh mô hình sau review PII', 'COMPLETED', 'f0d5354c-0c59-5e4e-816e-1310ff9a1181'::uuid, '2025-11-06 07:00:00+00:00', '2025-11-06 09:10:00+00:00', NULL, NULL, NULL, NULL, NULL, NULL, 'DATA_MODELING', NULL),
  ('7e621a51-f48a-53bf-927d-f415ae6c9249'::uuid, 'a678ac27-3077-5ef2-8919-5218b2e48791'::uuid, 'Bổ sung phân tích tỷ lệ lấp đầy kho', 'ACTIVE', '2d2884f5-138f-5885-8d75-38aff890d4d0'::uuid, '2026-08-10 08:30:00+00:00', '2026-08-10 09:20:00+00:00', NULL, NULL, NULL, NULL, NULL, NULL, 'DATA_MODELING', NULL),
  ('84bdeb46-0eba-564e-8437-833ede4e2718'::uuid, 'a678ac27-3077-5ef2-8919-5218b2e48791'::uuid, 'Thiết kế data mart lượt khám & chẩn đoán', 'ACTIVE', '3e80b14d-234b-550d-8103-dd9ef82ea1c8'::uuid, '2025-12-10 03:10:00+00:00', '2025-12-10 05:00:00+00:00', NULL, NULL, NULL, NULL, NULL, NULL, 'DATA_MODELING', NULL),
  ('b2f95613-a6f8-5e35-b6d7-e03bf1cc7aae'::uuid, '729525be-38aa-50fd-8ea9-3fedf76615f1'::uuid, 'Thiết kế DW rủi ro tín dụng - phiên 1', 'COMPLETED', '7ce4ee49-68c2-594a-b814-9c11c5eb0a6a'::uuid, '2025-11-08 02:00:00+00:00', '2025-11-08 05:30:00+00:00', NULL, NULL, NULL, NULL, NULL, NULL, 'DATA_MODELING', NULL),
  ('b2f95613-a6f8-5e35-b6d7-e03bf1cc7aae'::uuid, '0740e12f-bc1c-556f-9cc7-3ec5332e692e'::uuid, 'Rà soát mã hóa PII giao dịch', 'ACTIVE', '2b2907f2-91bf-578a-acb2-391081d6789e'::uuid, '2026-08-05 06:30:00+00:00', '2026-08-05 07:10:00+00:00', NULL, NULL, NULL, NULL, NULL, NULL, 'DATA_MODELING', NULL),
  ('54505703-ca04-5613-9f4a-d2499f12ee3d'::uuid, '0740e12f-bc1c-556f-9cc7-3ec5332e692e'::uuid, 'Thiết kế fact bán hàng đa kênh', 'COMPLETED', '7545fdc0-c3e9-55f7-8278-32cb3b18b6ac'::uuid, '2025-11-11 02:40:00+00:00', '2025-11-11 04:55:00+00:00', NULL, NULL, NULL, NULL, NULL, NULL, 'DATA_MODELING', NULL),
  ('18525676-8c6b-552b-8de7-a50899ef4b92'::uuid, 'c0445430-562e-5472-bea6-06f3a5d6f645'::uuid, 'Thiết kế fact vận đơn & hiệu suất tài xế', 'COMPLETED', '166e77f4-5a73-57b3-b9ba-eae00c1a688e'::uuid, '2025-11-18 04:10:00+00:00', '2025-11-18 06:20:00+00:00', NULL, NULL, NULL, NULL, NULL, NULL, 'DATA_MODELING', NULL),
  ('8dfcb679-8243-5be9-b8ee-b2bde7997277'::uuid, '15c1be82-ea36-5205-af17-7fb5947c2027'::uuid, 'Thiết kế mô hình học vụ & tốt nghiệp', 'ACTIVE', '2040ae41-afa0-57f5-8d4c-1bdd26ea2754'::uuid, '2025-12-02 02:10:00+00:00', '2025-12-02 03:40:00+00:00', NULL, NULL, NULL, NULL, NULL, NULL, 'DATA_MODELING', NULL),
  ('ef1e1ed3-a3b9-5fd0-86a5-2beec97bdf48'::uuid, '4c507932-ae90-57a1-8765-885e45eba112'::uuid, 'Thiết kế fact OEE theo dây chuyền', 'COMPLETED', '0c0a2c4f-c4f9-5f97-80d1-db681198f429'::uuid, '2025-12-08 06:30:00+00:00', '2025-12-08 08:45:00+00:00', NULL, NULL, NULL, NULL, NULL, NULL, 'DATA_MODELING', NULL),
  ('53774151-12ea-53d4-9d34-ebccfd4a2594'::uuid, '85651d6b-4cc0-56ba-ba15-ffc404f10abc'::uuid, 'Thiết kế DW bồi thường bảo hiểm', 'ARCHIVED', '16f05d9a-1837-559b-bdb3-42b3a1ec9d73'::uuid, '2025-10-20 01:30:00+00:00', '2025-12-01 03:00:00+00:00', NULL, NULL, NULL, NULL, NULL, NULL, 'DATA_MODELING', NULL),
  ('f8c4432f-0252-5275-a581-958039b98639'::uuid, 'e892c55a-77c6-5c8f-8e00-00da20839ba9'::uuid, 'Thiết kế fact churn thuê bao', 'ACTIVE', '73e590b3-2cd1-589f-b310-75beab465dfd'::uuid, '2025-12-15 03:00:00+00:00', '2025-12-15 05:15:00+00:00', NULL, NULL, NULL, NULL, NULL, NULL, 'DATA_MODELING', NULL),
  ('6268eced-f86b-5e52-b0a9-262a806879e9'::uuid, '25a6f954-f1cd-567d-88a0-630c4407b254'::uuid, 'Thiết kế DW hành vi mua sắm & marketing', 'ACTIVE', '2fdb8582-49bc-5285-9d5e-2fa613de7d70'::uuid, '2026-01-05 03:30:00+00:00', '2026-01-05 06:00:00+00:00', NULL, NULL, NULL, NULL, NULL, NULL, 'DATA_MODELING', NULL),
  ('0772523a-7235-410b-8eea-ee711baa62e0'::uuid, 'a678ac27-3077-5ef2-8919-5218b2e48791'::uuid, 'Untitled Session', 'ACTIVE', '90cc9a23-9e76-4980-9bdf-e6dd0d66085c'::uuid, '2026-08-22 14:46:48.761390+00:00', '2026-08-22 14:46:48.761395+00:00', NULL, NULL, NULL, NULL, NULL, NULL, 'DATA_MODELING', NULL),
  ('0772523a-7235-410b-8eea-ee711baa62e0'::uuid, 'a678ac27-3077-5ef2-8919-5218b2e48791'::uuid, 'Untitled Session', 'ACTIVE', '9bc9e68b-5272-4f67-a14f-33ff0215405c'::uuid, '2026-08-22 17:55:36.186606+00:00', '2026-08-22 17:55:36.186612+00:00', NULL, NULL, NULL, NULL, NULL, NULL, 'DATA_MODELING', NULL),
  ('0772523a-7235-410b-8eea-ee711baa62e0'::uuid, 'a678ac27-3077-5ef2-8919-5218b2e48791'::uuid, 'Phiên 1', 'ACTIVE', '1f88374e-e616-40d1-9796-582e438eca46'::uuid, '2026-08-22 14:49:26.643884+00:00', '2026-08-22 18:28:56.764746+00:00', NULL, NULL, NULL, NULL, NULL, NULL, 'DATA_MODELING', NULL),
  ('2da8c727-32f8-4ce2-9528-ae87ee60077d'::uuid, '01b19ecb-53ef-4373-99a5-3b0d8bd3af61'::uuid, 'Phiên test', 'ACTIVE', '4728efef-e781-4a7d-bd88-9b9b1edf56cb'::uuid, '2026-08-23 12:24:30.353220+00:00', '2026-08-24 09:04:02.165217+00:00', NULL, NULL, NULL, NULL, NULL, NULL, 'DATA_MODELING', NULL),
  ('c6e50b32-d59d-41d5-b634-618d8a4286c8'::uuid, '01b19ecb-53ef-4373-99a5-3b0d8bd3af61'::uuid, 'Requirement Clarification', 'COMPLETED', '200a1117-bbb4-4e9c-9be8-cb96cf01b2ee'::uuid, '2026-08-24 16:07:16.753770+00:00', '2026-08-24 16:08:05.734246+00:00', NULL, NULL, NULL, 'null', NULL, NULL, 'REQUIREMENT_CLARIFICATION', 1)
ON CONFLICT DO NOTHING;

-- Data for: session_events (64 rows)
INSERT INTO "session_events" ("session_id", "role", "type", "content", "metadata", "id", "created_at", "updated_at", "turn_id") VALUES
  ('9573f767-f342-56c0-90bc-c88ff63ee157'::uuid, 'USER', 'MESSAGE', 'Tôi cần xây dựng Data Warehouse cho dữ liệu hồ sơ bệnh án lưu trữ của bệnh viện, dựa trên yêu cầu và dữ liệu nguồn tôi đã tải lên.', NULL, '79cddbf9-b604-54a4-9714-d27c90949d05'::uuid, '2025-11-04 02:30:05+00:00', '2025-11-04 02:30:05+00:00', NULL),
  ('9573f767-f342-56c0-90bc-c88ff63ee157'::uuid, 'AGENT', 'MESSAGE', 'Đã nhận yêu cầu. Tôi sẽ điều phối các agent để phân tích requirement và dữ liệu nguồn trước khi thiết kế mô hình DW.', '{"model": "claude-sonnet-4-6"}', 'f01c1fee-1194-588b-9e1c-d40da8c5dcfb'::uuid, '2025-11-04 02:30:20+00:00', '2025-11-04 02:30:20+00:00', NULL),
  ('9573f767-f342-56c0-90bc-c88ff63ee157'::uuid, 'AGENT', 'AGENT_CALL', NULL, '{"input": {"project_id": "vimes-hs", "requirement_ids": ["req-vimes-hs-biz", "req-vimes-hs-an1", "req-vimes-hs-an2", "req-vimes-hs-tech"]}, "caller_agent": "OrchestrationAgent", "target_agent": "RequirementAgent"}', '2a7da704-99e7-5558-93b2-78a1fb8709bd'::uuid, '2025-11-04 02:30:25+00:00', '2025-11-04 02:30:25+00:00', NULL),
  ('9573f767-f342-56c0-90bc-c88ff63ee157'::uuid, 'AGENT', 'TOOL_CALL', NULL, '{"tool": "pii_guard.mask", "agent": "RequirementAgent", "arguments": {"target": "raw_requirement_text"}}', '756177e3-ba00-50f7-9d64-66aeb99864e9'::uuid, '2025-11-04 02:30:27+00:00', '2025-11-04 02:30:27+00:00', NULL),
  ('9573f767-f342-56c0-90bc-c88ff63ee157'::uuid, 'TOOL', 'TOOL_RESULT', NULL, '{"tool": "pii_guard.mask", "result": {"masked_fields": ["ho_ten", "dia_chi"], "masking_strategy": "hash_sha256"}, "status": "SUCCESS", "session_event_id": "756177e3-ba00-50f7-9d64-66aeb99864e9"}', 'af303b70-7247-5e8f-b034-ce29067dd1ea'::uuid, '2025-11-04 02:30:29+00:00', '2025-11-04 02:30:29+00:00', NULL),
  ('9573f767-f342-56c0-90bc-c88ff63ee157'::uuid, 'AGENT', 'AGENT_RESULT', NULL, '{"llm": {"model": "claude-sonnet-4-6", "provider": "anthropic", "latency_ms": 3120, "temperature": 0.3, "input_tokens": 2140, "total_tokens": 2620, "finish_reason": "end_turn", "output_tokens": 480}, "agent": "RequirementAgent", "output": {"metrics": ["Số lượng hồ sơ lưu trữ", "Tỷ lệ lấp đầy vị trí lưu trữ"], "analytical_requirements_extracted": 2}, "status": "SUCCESS", "session_event_id": "af303b70-7247-5e8f-b034-ce29067dd1ea"}', '6a186d5f-81ac-54a5-801e-e4743cc62784'::uuid, '2025-11-04 02:31:10+00:00', '2025-11-04 02:31:10+00:00', NULL),
  ('9573f767-f342-56c0-90bc-c88ff63ee157'::uuid, 'AGENT', 'AGENT_CALL', NULL, '{"input": {"data_source_ids": ["ds-vimes-hs-main", "ds-vimes-hs-master"]}, "caller_agent": "OrchestrationAgent", "target_agent": "SourceDataAgent"}', '77c5d40e-1963-5407-9e96-fcd96c7c480d'::uuid, '2025-11-04 02:31:15+00:00', '2025-11-04 02:31:15+00:00', NULL),
  ('9573f767-f342-56c0-90bc-c88ff63ee157'::uuid, 'AGENT', 'TOOL_CALL', NULL, '{"tool": "schema_inspector.extract", "agent": "SourceDataAgent", "arguments": {"source": "ds-vimes-hs-main", "sample_rows": 500}}', '5f3a07da-71c7-5ca3-a7a3-edf97b45a56a'::uuid, '2025-11-04 02:31:18+00:00', '2025-11-04 02:31:18+00:00', NULL),
  ('9573f767-f342-56c0-90bc-c88ff63ee157'::uuid, 'TOOL', 'TOOL_RESULT', NULL, '{"tool": "schema_inspector.extract", "result": {"tables_found": 11, "pii_columns_detected": ["ho_ten", "dia_chi", "ten_benh_nhan"]}, "status": "SUCCESS", "session_event_id": "5f3a07da-71c7-5ca3-a7a3-edf97b45a56a"}', '514c907a-e6bf-56da-b136-d1f211a049db'::uuid, '2025-11-04 02:31:40+00:00', '2025-11-04 02:31:40+00:00', NULL),
  ('9573f767-f342-56c0-90bc-c88ff63ee157'::uuid, 'AGENT', 'AGENT_RESULT', NULL, '{"llm": {"model": "claude-sonnet-4-6", "provider": "anthropic", "latency_ms": 4870, "temperature": 0.2, "input_tokens": 5230, "total_tokens": 6140, "finish_reason": "end_turn", "output_tokens": 910}, "agent": "SourceDataAgent", "output": {"tables_analyzed": 11, "relationships_inferred": 12}, "status": "SUCCESS", "session_event_id": "514c907a-e6bf-56da-b136-d1f211a049db"}', '30098c13-275c-5ef8-a4f5-839ea875480a'::uuid, '2025-11-04 02:32:30+00:00', '2025-11-04 02:32:30+00:00', NULL),
  ('9573f767-f342-56c0-90bc-c88ff63ee157'::uuid, 'AGENT', 'AGENT_CALL', NULL, '{"input": {"source_tables": 11, "analytical_requirements": 2}, "caller_agent": "OrchestrationAgent", "target_agent": "DWDesignAgent"}', '2eca7814-84de-5cfa-a4c1-07b353e262fa'::uuid, '2025-11-04 02:32:35+00:00', '2025-11-04 02:32:35+00:00', NULL),
  ('9573f767-f342-56c0-90bc-c88ff63ee157'::uuid, 'AGENT', 'AGENT_RESULT', NULL, '{"llm": {"model": "claude-sonnet-4-6", "provider": "anthropic", "latency_ms": 9210, "temperature": 0.4, "input_tokens": 8900, "total_tokens": 11000, "finish_reason": "end_turn", "output_tokens": 2100}, "agent": "DWDesignAgent", "output": {"dim_tables": 6, "fact_tables": ["fact_ho_so_luu_tru"], "dbml_generated": true}, "status": "SUCCESS", "session_event_id": "2eca7814-84de-5cfa-a4c1-07b353e262fa"}', '24badbbf-fadb-5dd9-95b0-2893cddaa750'::uuid, '2025-11-04 02:35:00+00:00', '2025-11-04 02:35:00+00:00', NULL),
  ('9573f767-f342-56c0-90bc-c88ff63ee157'::uuid, 'AGENT', 'TOOL_CALL', NULL, '{"tool": "dbml_validate", "agent": "ValidationEngine", "arguments": {"revision_candidate": 1}}', 'c239f853-5a7b-50cc-ae88-a9479ec3b8ce'::uuid, '2025-11-04 02:35:05+00:00', '2025-11-04 02:35:05+00:00', NULL),
  ('9573f767-f342-56c0-90bc-c88ff63ee157'::uuid, 'TOOL', 'TOOL_RESULT', NULL, '{"tool": "dbml_validate", "error": "Syntax error: table ''dim_khoa'' thiếu dấu đóng ngoặc tại dòng 42", "status": "FAILED", "session_event_id": "c239f853-5a7b-50cc-ae88-a9479ec3b8ce"}', '02f5aa98-c649-5444-a8f8-8fa7324d08ac'::uuid, '2025-11-04 02:35:08+00:00', '2025-11-04 02:35:08+00:00', NULL),
  ('9573f767-f342-56c0-90bc-c88ff63ee157'::uuid, 'AGENT', 'MESSAGE', 'Phát hiện lỗi cú pháp DBML, đang yêu cầu DWDesignAgent tái tạo lại thiết kế (retry).', '{"model": "claude-sonnet-4-6"}', '44e69970-bd43-5ed4-8cea-0fc4b60a980a'::uuid, '2025-11-04 02:35:12+00:00', '2025-11-04 02:35:12+00:00', NULL),
  ('9573f767-f342-56c0-90bc-c88ff63ee157'::uuid, 'AGENT', 'TOOL_CALL', NULL, '{"tool": "dbml_validate", "agent": "ValidationEngine", "arguments": {"attempt": 2, "revision_candidate": 1}}', '0214f42b-4fd1-55e2-bcfe-55b9ba605ad1'::uuid, '2025-11-04 02:36:40+00:00', '2025-11-04 02:36:40+00:00', NULL),
  ('9573f767-f342-56c0-90bc-c88ff63ee157'::uuid, 'TOOL', 'TOOL_RESULT', NULL, '{"tool": "dbml_validate", "result": {"warnings": 0, "syntax_ok": true}, "status": "SUCCESS", "session_event_id": "0214f42b-4fd1-55e2-bcfe-55b9ba605ad1"}', 'be584b6f-ed17-52b6-b510-21e9d979f591'::uuid, '2025-11-04 02:36:43+00:00', '2025-11-04 02:36:43+00:00', NULL),
  ('9573f767-f342-56c0-90bc-c88ff63ee157'::uuid, 'AGENT', 'TOOL_CALL', NULL, '{"tool": "sandbox_run_ddl", "agent": "Sandbox", "arguments": {"revision_candidate": 1}}', 'db1a3414-faa1-5de0-9587-a0baab72a90e'::uuid, '2025-11-04 02:36:50+00:00', '2025-11-04 02:36:50+00:00', NULL),
  ('9573f767-f342-56c0-90bc-c88ff63ee157'::uuid, 'TOOL', 'TOOL_RESULT', NULL, '{"tool": "sandbox_run_ddl", "result": {"runtime_errors": 0, "tables_created": 7, "sample_load_rows": 1000}, "status": "SUCCESS", "session_event_id": "db1a3414-faa1-5de0-9587-a0baab72a90e"}', 'bfff9800-e79a-52d9-aaa9-8ef0bc33d280'::uuid, '2025-11-04 02:38:15+00:00', '2025-11-04 02:38:15+00:00', NULL),
  ('9573f767-f342-56c0-90bc-c88ff63ee157'::uuid, 'AGENT', 'QUESTION', 'Sandbox chạy thành công. Trường ''so_ho_so'' nên được coi là khóa chính của fact_ho_so_luu_tru hay chỉ là khóa ngoại tới dim_benh_nhan? Vui lòng xác nhận để hoàn tất thiết kế.', NULL, '5b039e0f-ae7e-5ca3-88ba-0218aeb15834'::uuid, '2025-11-04 04:20:00+00:00', '2025-11-04 04:20:00+00:00', NULL),
  ('9573f767-f342-56c0-90bc-c88ff63ee157'::uuid, 'USER', 'ANSWER', 'so_ho_so nên là khóa ngoại tới dim_benh_nhan (đã ẩn danh). Khóa chính của fact nên là so_benh_an vì mỗi đợt điều trị mới sinh 1 dòng fact.', NULL, '60687b38-f36e-526c-a10d-15a268a1a0da'::uuid, '2025-11-04 04:32:00+00:00', '2025-11-04 04:32:00+00:00', NULL),
  ('9573f767-f342-56c0-90bc-c88ff63ee157'::uuid, 'AGENT', 'MESSAGE', 'Đã cập nhật thiết kế theo xác nhận của bạn. DBML đã sẵn sàng để chuyển sang HumanReview.', '{"model": "claude-sonnet-4-6"}', 'e166ed48-914d-5541-a0c5-45ba8af250d6'::uuid, '2025-11-04 04:45:00+00:00', '2025-11-04 04:45:00+00:00', NULL),
  ('2d2884f5-138f-5885-8d75-38aff890d4d0'::uuid, 'USER', 'MESSAGE', 'Bổ sung thêm phân tích tỷ lệ lấp đầy Kho/Tủ/Ngăn vào mô hình hiện tại.', NULL, '9bda8727-7b6f-5a6c-82ca-8e79b17cf580'::uuid, '2026-08-10 08:30:10+00:00', '2026-08-10 08:30:10+00:00', NULL),
  ('2d2884f5-138f-5885-8d75-38aff890d4d0'::uuid, 'AGENT', 'AGENT_CALL', NULL, '{"input": {"base_revision": 2, "new_analytical_requirement": "req-vimes-hs-an2"}, "caller_agent": "OrchestrationAgent", "target_agent": "DWDesignAgent"}', '049ca70d-6ea9-566f-a9c3-37edd88f7a4a'::uuid, '2026-08-10 08:31:00+00:00', '2026-08-10 08:31:00+00:00', NULL),
  ('2d2884f5-138f-5885-8d75-38aff890d4d0'::uuid, 'AGENT', 'AGENT_RESULT', NULL, '{"llm": {"model": "claude-sonnet-4-6", "provider": "anthropic", "latency_ms": 6300, "temperature": 0.4, "input_tokens": 6100, "total_tokens": 7550, "finish_reason": "end_turn", "output_tokens": 1450}, "agent": "DWDesignAgent", "output": {"dbml_generated": true, "new_fact_tables": ["fact_ton_kho_vi_tri"]}, "status": "SUCCESS", "session_event_id": "049ca70d-6ea9-566f-a9c3-37edd88f7a4a"}', '2c431c61-d309-5346-a097-10e9b7854955'::uuid, '2026-08-10 08:36:00+00:00', '2026-08-10 08:36:00+00:00', NULL),
  ('4728efef-e781-4a7d-bd88-9b9b1edf56cb'::uuid, 'USER', 'MESSAGE', 'Bệnh viện muốn theo dõi số lượng', 'null', 'd3623028-82fa-4b92-ac8d-d02406f5f562'::uuid, '2026-08-24 09:03:10.034283+00:00', '2026-08-24 09:03:10.034287+00:00', 'a06c0979-414e-42c7-a5f3-24fe0996f1ee'::uuid),
  ('2d2884f5-138f-5885-8d75-38aff890d4d0'::uuid, 'AGENT', 'MESSAGE', 'Đã tạo đề xuất thay đổi (data_model_change) với base_revision=2, đang chờ bạn Accept/Reject trong HumanReview.', '{"model": "claude-sonnet-4-6"}', '471c9e38-dfbe-5ac3-b927-475423c07c6b'::uuid, '2026-08-10 09:20:00+00:00', '2026-08-10 09:20:00+00:00', NULL),
  ('7ce4ee49-68c2-594a-b814-9c11c5eb0a6a'::uuid, 'USER', 'MESSAGE', 'Thiết kế DW cho phân tích rủi ro tín dụng dựa trên dữ liệu Core Banking và CRM.', NULL, 'c719c25c-effb-5382-9f22-6a17993b2738'::uuid, '2025-11-08 02:00:10+00:00', '2025-11-08 02:00:10+00:00', NULL),
  ('7ce4ee49-68c2-594a-b814-9c11c5eb0a6a'::uuid, 'AGENT', 'AGENT_CALL', NULL, '{"input": {"data_source_ids": ["ds-bank-core", "ds-bank-crm"]}, "caller_agent": "OrchestrationAgent", "target_agent": "SourceDataAgent"}', '6d8129d9-371b-502c-8896-08b5a4767866'::uuid, '2025-11-08 02:00:30+00:00', '2025-11-08 02:00:30+00:00', NULL),
  ('7ce4ee49-68c2-594a-b814-9c11c5eb0a6a'::uuid, 'AGENT', 'AGENT_RESULT', NULL, '{"agent": "SourceDataAgent", "error": "Agent execution was cancelled", "status": "CANCELLED", "session_event_id": "6d8129d9-371b-502c-8896-08b5a4767866"}', 'fb4411d2-9f3c-56fc-abee-16cfdebf1413'::uuid, '2025-11-08 02:05:00+00:00', '2025-11-08 02:05:00+00:00', NULL),
  ('7ce4ee49-68c2-594a-b814-9c11c5eb0a6a'::uuid, 'USER', 'MESSAGE', 'Xin lỗi, tôi bấm nhầm huỷ. Vui lòng chạy lại phân tích nguồn dữ liệu.', NULL, '83323f96-8bca-5f73-8a68-1ca60f7e5876'::uuid, '2025-11-08 02:06:00+00:00', '2025-11-08 02:06:00+00:00', NULL),
  ('7ce4ee49-68c2-594a-b814-9c11c5eb0a6a'::uuid, 'AGENT', 'AGENT_CALL', NULL, '{"input": {"retry": true, "data_source_ids": ["ds-bank-core", "ds-bank-crm"]}, "caller_agent": "OrchestrationAgent", "target_agent": "SourceDataAgent"}', 'aff7f2b6-2314-5d19-b6dd-d813bd1ff98a'::uuid, '2025-11-08 02:06:10+00:00', '2025-11-08 02:06:10+00:00', NULL),
  ('7ce4ee49-68c2-594a-b814-9c11c5eb0a6a'::uuid, 'AGENT', 'AGENT_RESULT', NULL, '{"llm": {"model": "claude-sonnet-4-6", "provider": "anthropic", "latency_ms": 3900, "temperature": 0.2, "input_tokens": 3400, "total_tokens": 4100, "finish_reason": "end_turn", "output_tokens": 700}, "agent": "SourceDataAgent", "output": {"tables_analyzed": 4, "relationships_inferred": 3}, "status": "SUCCESS", "session_event_id": "aff7f2b6-2314-5d19-b6dd-d813bd1ff98a"}', 'd4b8c311-da6a-55d3-96f6-5879c3005b27'::uuid, '2025-11-08 02:09:00+00:00', '2025-11-08 02:09:00+00:00', NULL),
  ('7ce4ee49-68c2-594a-b814-9c11c5eb0a6a'::uuid, 'AGENT', 'MESSAGE', 'Hoàn tất thiết kế DW rủi ro tín dụng phiên bản đầu tiên, đã qua Validate và Sandbox thành công.', '{"model": "claude-sonnet-4-6"}', 'e98051d3-fb36-57d3-87b5-f4c0e009f4bd'::uuid, '2025-11-08 05:30:00+00:00', '2025-11-08 05:30:00+00:00', NULL),
  ('7545fdc0-c3e9-55f7-8278-32cb3b18b6ac'::uuid, 'USER', 'MESSAGE', 'Thiết kế fact bán hàng đa kênh hợp nhất từ POS và sàn TMĐT nội bộ.', NULL, '4392641e-b672-5971-9d7b-0075773e3991'::uuid, '2025-11-11 02:40:05+00:00', '2025-11-11 02:40:05+00:00', NULL),
  ('7545fdc0-c3e9-55f7-8278-32cb3b18b6ac'::uuid, 'AGENT', 'TOOL_CALL', NULL, '{"tool": "dbml_validate", "agent": "ValidationEngine", "arguments": {"revision_candidate": 1}}', '64462410-dec0-5f87-8ca7-baed27c864d2'::uuid, '2025-11-11 04:40:00+00:00', '2025-11-11 04:40:00+00:00', NULL),
  ('7545fdc0-c3e9-55f7-8278-32cb3b18b6ac'::uuid, 'TOOL', 'TOOL_RESULT', NULL, '{"tool": "dbml_validate", "result": {"warnings": 1, "syntax_ok": true}, "status": "SUCCESS", "session_event_id": "64462410-dec0-5f87-8ca7-baed27c864d2"}', '457e4bb4-d6ff-5b12-a68f-24dc9dca80cb'::uuid, '2025-11-11 04:40:05+00:00', '2025-11-11 04:40:05+00:00', NULL),
  ('7545fdc0-c3e9-55f7-8278-32cb3b18b6ac'::uuid, 'AGENT', 'MESSAGE', 'Thiết kế fact_doanh_thu_ban_hang đã sẵn sàng, chuyển sang HumanReview.', '{"model": "claude-sonnet-4-6"}', 'a03deaae-d681-5104-908a-1ec310fcb772'::uuid, '2025-11-11 04:55:00+00:00', '2025-11-11 04:55:00+00:00', NULL),
  ('1f88374e-e616-40d1-9796-582e438eca46'::uuid, 'USER', 'MESSAGE', 'Các bảng bị thiếu liên kết rồi, thêm liên kết vào hộ tôi', 'null', 'e5ad8d7d-e0a5-4554-ae4e-0dd2ba908271'::uuid, '2026-08-22 14:51:34.401794+00:00', '2026-08-22 14:51:34.401798+00:00', 'a7b0b9fb-2bff-47a9-a962-7788063e6bc5'::uuid),
  ('1f88374e-e616-40d1-9796-582e438eca46'::uuid, 'AGENT', 'AGENT_CALL', NULL, '{"input": "session-conversation", "caller_agent": "OrchestratorAgent", "target_agent": "DWDesignAgent"}', '40d70698-d4e5-410a-83f6-1fa9b5ff522b'::uuid, '2026-08-22 14:51:34.385197+00:00', '2026-08-22 14:51:34.385201+00:00', 'a7b0b9fb-2bff-47a9-a962-7788063e6bc5'::uuid),
  ('1f88374e-e616-40d1-9796-582e438eca46'::uuid, 'AGENT', 'AGENT_RESULT', 'Agent could not complete this turn.', '{"llm": null, "agent": "DWDesignAgent", "error": null, "output": null, "status": "FAILED", "session_event_id": "40d70698-d4e5-410a-83f6-1fa9b5ff522b"}', '7de633ef-2e9a-45d1-b405-7db3d5aa80ab'::uuid, '2026-08-22 14:51:34.501398+00:00', '2026-08-22 14:51:34.501401+00:00', 'a7b0b9fb-2bff-47a9-a962-7788063e6bc5'::uuid),
  ('1f88374e-e616-40d1-9796-582e438eca46'::uuid, 'USER', 'MESSAGE', 'Các bảng bị thiếu liên kết rồi, thêm liên kết vào hộ tôi', 'null', '4520d0f1-468f-4410-bab2-bdf8c92ce997'::uuid, '2026-08-22 16:24:37.536180+00:00', '2026-08-22 16:24:37.536187+00:00', '909ec76e-ae6d-4d5e-90a5-016347497053'::uuid),
  ('1f88374e-e616-40d1-9796-582e438eca46'::uuid, 'AGENT', 'AGENT_CALL', NULL, '{"input": "session-conversation", "caller_agent": "OrchestratorAgent", "target_agent": "DWDesignAgent"}', '7b9efdd3-9443-42ef-a4c9-dd6260637f0c'::uuid, '2026-08-22 16:24:37.513004+00:00', '2026-08-22 16:24:37.513006+00:00', '909ec76e-ae6d-4d5e-90a5-016347497053'::uuid),
  ('1f88374e-e616-40d1-9796-582e438eca46'::uuid, 'AGENT', 'AGENT_RESULT', 'The proposal is ready for review.', '{"llm": null, "agent": "DWDesignAgent", "error": null, "output": "f8f4f428-f0bc-4057-8eb0-9cf8052959cb", "status": "SUCCESS", "session_event_id": "7b9efdd3-9443-42ef-a4c9-dd6260637f0c"}', 'd518818e-a2ab-491e-9b27-5d922796d7ef'::uuid, '2026-08-22 16:25:03.686418+00:00', '2026-08-22 16:25:03.686423+00:00', '909ec76e-ae6d-4d5e-90a5-016347497053'::uuid),
  ('1f88374e-e616-40d1-9796-582e438eca46'::uuid, 'USER', 'MESSAGE', 'Các bảng bị thiếu liên kết rồi, thêm liên kết vào hộ tôi', 'null', '533cfceb-79cc-4817-a610-47c8b46947d9'::uuid, '2026-08-22 18:28:27.059902+00:00', '2026-08-22 18:28:27.059908+00:00', '1ff84f9f-a77d-42fa-a04d-b4f690777e18'::uuid),
  ('1f88374e-e616-40d1-9796-582e438eca46'::uuid, 'AGENT', 'AGENT_CALL', NULL, '{"input": "session-conversation", "caller_agent": "OrchestratorAgent", "target_agent": "DWDesignAgent"}', 'd3e58ef7-0ed7-4e9e-b44b-b0aec073c29f'::uuid, '2026-08-22 18:28:27.043054+00:00', '2026-08-22 18:28:27.043056+00:00', '1ff84f9f-a77d-42fa-a04d-b4f690777e18'::uuid),
  ('1f88374e-e616-40d1-9796-582e438eca46'::uuid, 'AGENT', 'AGENT_RESULT', 'Đã bổ sung đầy đủ các mối liên kết khóa ngoại (Ref) giữa hai bảng sự kiện (Fact_DieuTri, Fact_LuuTruHoSo) và các bảng chiều (Dimension) trong mô hình Star Schema.', '{"llm": null, "agent": "DWDesignAgent", "error": null, "output": "c5069575-fb9c-4e2d-b09c-3350c449effe", "status": "SUCCESS", "session_event_id": "d3e58ef7-0ed7-4e9e-b44b-b0aec073c29f"}', '07533ca3-9e9e-4894-9745-04e1579ea61d'::uuid, '2026-08-22 18:28:56.764694+00:00', '2026-08-22 18:28:56.764700+00:00', '1ff84f9f-a77d-42fa-a04d-b4f690777e18'::uuid),
  ('4728efef-e781-4a7d-bd88-9b9b1edf56cb'::uuid, 'USER', 'MESSAGE', 'Các bảng bị mất liên kết rồi, thêm liên kết vào cho tôi.', 'null', '1cc86086-9b6c-4a93-b28d-3546e086a6b2'::uuid, '2026-08-23 12:25:35.644990+00:00', '2026-08-23 12:25:35.644995+00:00', 'b27f20b4-8d6e-4ad8-a334-8b1a07c7b630'::uuid),
  ('4728efef-e781-4a7d-bd88-9b9b1edf56cb'::uuid, 'AGENT', 'AGENT_CALL', NULL, '{"input": "session-conversation", "caller_agent": "OrchestratorAgent", "target_agent": "DWDesignAgent"}', '178d494b-bded-4df9-8ecb-5e2b091b5f24'::uuid, '2026-08-23 12:25:35.637478+00:00', '2026-08-23 12:25:35.637481+00:00', 'b27f20b4-8d6e-4ad8-a334-8b1a07c7b630'::uuid),
  ('4728efef-e781-4a7d-bd88-9b9b1edf56cb'::uuid, 'AGENT', 'AGENT_RESULT', 'Agent could not complete this turn.', '{"llm": null, "agent": "DWDesignAgent", "error": null, "output": null, "status": "FAILED", "session_event_id": "178d494b-bded-4df9-8ecb-5e2b091b5f24"}', '8215e4ed-6f86-44fa-ac3d-ac86dfef44ee'::uuid, '2026-08-23 12:26:26.113695+00:00', '2026-08-23 12:26:26.113698+00:00', 'b27f20b4-8d6e-4ad8-a334-8b1a07c7b630'::uuid)
ON CONFLICT DO NOTHING;

INSERT INTO "session_events" ("session_id", "role", "type", "content", "metadata", "id", "created_at", "updated_at", "turn_id") VALUES
  ('4728efef-e781-4a7d-bd88-9b9b1edf56cb'::uuid, 'USER', 'MESSAGE', 'Các bảng bị mất liên kết rồi, thêm liên kết vào cho tôi.', 'null', '4c268e3f-bff2-4931-b0af-ea75ae63b2f4'::uuid, '2026-08-23 12:42:57.820751+00:00', '2026-08-23 12:42:57.820756+00:00', '947ebc19-fa12-456f-99aa-0439c7ccf00c'::uuid),
  ('4728efef-e781-4a7d-bd88-9b9b1edf56cb'::uuid, 'AGENT', 'AGENT_CALL', NULL, '{"input": "session-conversation", "caller_agent": "OrchestratorAgent", "target_agent": "DWDesignAgent"}', '66303749-634d-4204-b4b1-86df0a0a4fba'::uuid, '2026-08-23 12:42:57.811472+00:00', '2026-08-23 12:42:57.811472+00:00', '947ebc19-fa12-456f-99aa-0439c7ccf00c'::uuid),
  ('4728efef-e781-4a7d-bd88-9b9b1edf56cb'::uuid, 'AGENT', 'AGENT_RESULT', 'Đã thiết lập đầy đủ liên kết khóa ngoại giữa các bảng Fact và các bảng Dimension trong mô hình dữ liệu.', '{"llm": null, "agent": "DWDesignAgent", "error": null, "output": "a214af38-c5a2-49e3-9148-46fa2dea28f0", "status": "SUCCESS", "session_event_id": "66303749-634d-4204-b4b1-86df0a0a4fba"}', '33faa001-1106-41af-8b3a-0a9bacf24773'::uuid, '2026-08-23 12:43:22.545615+00:00', '2026-08-23 12:43:22.545621+00:00', '947ebc19-fa12-456f-99aa-0439c7ccf00c'::uuid),
  ('4728efef-e781-4a7d-bd88-9b9b1edf56cb'::uuid, 'USER', 'MESSAGE', 'Bệnh viện muốn phân tích số lượng bệnh nhân theo thời gian để theo dõi xu hướng khám chữa bệnh.', 'null', '22ce3cdc-6aa8-439d-aeba-1448d09d70a2'::uuid, '2026-08-24 08:17:44.210449+00:00', '2026-08-24 08:17:44.210455+00:00', '8f58659e-7f51-42c7-b870-2676dd6475a9'::uuid),
  ('4728efef-e781-4a7d-bd88-9b9b1edf56cb'::uuid, 'AGENT', 'AGENT_CALL', NULL, '{"input": "session-conversation", "caller_agent": "OrchestratorAgent", "target_agent": "DWDesignAgent"}', 'b18a1834-404f-4c3c-a0f4-ad03bb77b32c'::uuid, '2026-08-24 08:17:44.191081+00:00', '2026-08-24 08:17:44.191082+00:00', '8f58659e-7f51-42c7-b870-2676dd6475a9'::uuid),
  ('4728efef-e781-4a7d-bd88-9b9b1edf56cb'::uuid, 'AGENT', 'AGENT_RESULT', 'Mô hình dữ liệu hiện tại đã đáp ứng đầy đủ yêu cầu phân tích số lượng bệnh nhân và xu hướng khám chữa bệnh theo thời gian.', '{"llm": null, "agent": "DWDesignAgent", "error": null, "output": "83b8c13e-76ee-4c35-b130-fd492a5fc23f", "status": "SUCCESS", "session_event_id": "b18a1834-404f-4c3c-a0f4-ad03bb77b32c"}', '67efeecc-d3be-4e08-9a87-e3a232a04a54'::uuid, '2026-08-24 08:18:18.153046+00:00', '2026-08-24 08:18:18.153050+00:00', '8f58659e-7f51-42c7-b870-2676dd6475a9'::uuid),
  ('4728efef-e781-4a7d-bd88-9b9b1edf56cb'::uuid, 'AGENT', 'AGENT_CALL', NULL, '{"input": "session-conversation", "caller_agent": "OrchestratorAgent", "target_agent": "DWDesignAgent"}', 'd112ed8b-59dd-48d9-975a-ae09aeaad888'::uuid, '2026-08-24 09:03:10.024629+00:00', '2026-08-24 09:03:10.024630+00:00', 'a06c0979-414e-42c7-a5f3-24fe0996f1ee'::uuid),
  ('4728efef-e781-4a7d-bd88-9b9b1edf56cb'::uuid, 'AGENT', 'AGENT_RESULT', 'Mô hình dữ liệu hiện tại đã đáp ứng đầy đủ việc theo dõi số lượng bệnh nhân và hồ sơ theo thời gian cũng như các chiều phân tích liên quan.', '{"llm": null, "agent": "DWDesignAgent", "error": null, "output": null, "status": "SUCCESS", "session_event_id": "d112ed8b-59dd-48d9-975a-ae09aeaad888"}', '15167944-dd9f-4dca-ba0e-056bd2a180d6'::uuid, '2026-08-24 09:03:19.743896+00:00', '2026-08-24 09:03:19.743902+00:00', 'a06c0979-414e-42c7-a5f3-24fe0996f1ee'::uuid),
  ('4728efef-e781-4a7d-bd88-9b9b1edf56cb'::uuid, 'USER', 'MESSAGE', 'Bạn không hỏi tôi số lượng gì à?', 'null', '348176c5-cf0c-4714-a4a2-846bea318678'::uuid, '2026-08-24 09:03:47.140142+00:00', '2026-08-24 09:03:47.140148+00:00', '97c3b3d6-2611-41ee-88aa-a743b958e1a0'::uuid),
  ('4728efef-e781-4a7d-bd88-9b9b1edf56cb'::uuid, 'AGENT', 'AGENT_CALL', NULL, '{"input": "session-conversation", "caller_agent": "OrchestratorAgent", "target_agent": "DWDesignAgent"}', '4d732112-a5b3-4506-95c2-cef9d9501b5f'::uuid, '2026-08-24 09:03:47.133239+00:00', '2026-08-24 09:03:47.133240+00:00', '97c3b3d6-2611-41ee-88aa-a743b958e1a0'::uuid),
  ('4728efef-e781-4a7d-bd88-9b9b1edf56cb'::uuid, 'AGENT', 'AGENT_RESULT', 'Mô hình dữ liệu hiện tại được giữ nguyên vì tin nhắn không chứa yêu cầu điều chỉnh cấu trúc.', '{"llm": null, "agent": "DWDesignAgent", "error": null, "output": null, "status": "SUCCESS", "session_event_id": "4d732112-a5b3-4506-95c2-cef9d9501b5f"}', '9ba0490c-322b-46a4-b1c4-684a9bfc48b4'::uuid, '2026-08-24 09:04:02.165180+00:00', '2026-08-24 09:04:02.165185+00:00', '97c3b3d6-2611-41ee-88aa-a743b958e1a0'::uuid),
  ('200a1117-bbb4-4e9c-9be8-cb96cf01b2ee'::uuid, 'AGENT', 'AGENT_CALL', NULL, '{"input": "requirement-clarification", "caller_agent": "OrchestratorAgent", "target_agent": "RequirementAgent"}', '878c976f-5193-444f-868f-65d73d00266d'::uuid, '2026-08-24 16:07:16.756015+00:00', '2026-08-24 16:07:16.756021+00:00', '120e2fd5-8577-4170-9874-cc4168b33d6e'::uuid),
  ('200a1117-bbb4-4e9c-9be8-cb96cf01b2ee'::uuid, 'AGENT', 'AGENT_RESULT', 'Đã xác định đầy đủ các yêu cầu nghiệp vụ và yêu cầu phân tích dữ liệu đối với Data Warehouse quản lý bán thuốc và cấp phát đơn thuốc tại bệnh viện.', '{"llm": null, "agent": "RequirementAgent", "error": null, "output": "revision=1;status=READY", "status": "SUCCESS", "session_event_id": "878c976f-5193-444f-868f-65d73d00266d"}', '3557a325-71c4-40b7-a015-817713bf06c1'::uuid, '2026-08-24 16:07:26.804188+00:00', '2026-08-24 16:07:26.804194+00:00', '120e2fd5-8577-4170-9874-cc4168b33d6e'::uuid),
  ('200a1117-bbb4-4e9c-9be8-cb96cf01b2ee'::uuid, 'AGENT', 'MESSAGE', 'Đã xác định đầy đủ các yêu cầu nghiệp vụ và yêu cầu phân tích dữ liệu đối với Data Warehouse quản lý bán thuốc và cấp phát đơn thuốc tại bệnh viện.', '{"model": null, "agent_result_id": "3557a325-71c4-40b7-a015-817713bf06c1", "proposal_change_id": null}', 'f662a3e9-f56e-4d34-b01d-5c0647139922'::uuid, '2026-08-24 16:07:26.816419+00:00', '2026-08-24 16:07:26.816422+00:00', '120e2fd5-8577-4170-9874-cc4168b33d6e'::uuid)
ON CONFLICT DO NOTHING;

-- Data for: sandbox_configs (2 rows)
INSERT INTO "sandbox_configs" ("project_id", "db_type", "host", "port", "database_name", "username", "password", "schema_name", "id", "created_at", "updated_at") VALUES
  ('0772523a-7235-410b-8eea-ee711baa62e0'::uuid, 'POSTGRESQL', '127.0.0.1', 5434, 'sandbox_db', 'postgres', 'fernet:gAAAAABqigPQY5KSz6ygWsHroUcmD4kl4xj-sxGT5Fqy-5y4kfBmOt8dvHVEEuL8mnb3z6LYbtHg3Euf8wEooXzqO6ptIXE_LQ==', 'test_db', 'b8d28053-9f74-4811-8326-3277530acbc9'::uuid, '2026-08-22 11:19:40.530750+00:00', '2026-08-22 20:17:20.147015+00:00'),
  ('2da8c727-32f8-4ce2-9528-ae87ee60077d'::uuid, 'POSTGRESQL', '127.0.0.1', 5434, 'sandbox_db', 'postgres', 'fernet:gAAAAABqiux-_-FxGGZLKavZtQxAZTO1DAvNStDfFtdQUXbufcn94EJ2sqHoLwA1PAxFtoXc8sCCBr1Jtacbfb7G8yRSfVLdag==', 'test_db', '53e68ad6-c6cf-4139-8fac-1c556f5ed442'::uuid, '2026-08-23 12:49:27.214370+00:00', '2026-08-23 12:50:06.568023+00:00')
ON CONFLICT DO NOTHING;

COMMIT;