```dbml
Project data14_multi_agent {
  database_type: "PostgreSQL"
  Note: "Database for Multi-Agent system that transforms Business Requirements into Data Warehouse / Data Model"
}

// ============================================================
// 1. USER & PROJECT MANAGEMENT
// ============================================================

Table users {
  id uuid [pk]
  username varchar(100) [not null, unique]
  email varchar(255) [not null, unique]
  created_at timestamp [not null]
  updated_at timestamp [not null]
}

Table projects {
  id uuid [pk]
  name varchar(255) [not null]
  description text
  domain varchar(100) [note: 'Lĩnh vực nghiệp vụ, VD: Y tế']
  requirement text [not null, note: 'Raw requirement do người dùng nhập']
  status varchar(30) [not null, default: 'ACTIVE', note: 'ACTIVE, ANALYZING, ARCHIVED (lưu trữ từ trạng thái ACTIVE)']
  user_id uuid [not null]
  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    user_id
    status
  }
}

Table project_members {
  id uuid [pk]

  project_id uuid [not null]
  user_id uuid [not null]

  role varchar(30) [not null, note: 'OWNER, MEMBER']

  joined_at timestamp [not null]

  indexes {
    project_id
    user_id
    (project_id, user_id) [unique]
  }
}

Ref: project_members.project_id > projects.id
Ref: project_members.user_id > users.id


// ============================================================
// 2. REQUIREMENTS
// ============================================================

Table requirements {
  id uuid [pk]

  project_id uuid [not null]

  type varchar(50) [not null,
    note: 'BUSINESS, ANALYTICAL, TECHNICAL'
  ]
  // BUSINESS: Doanh nghiệp muốn đạt gì?
  //   VD: Theo dõi hiệu quả hoạt động bệnh viện
  //
  // ANALYTICAL: Cần phân tích gì?
  //   VD: Phân tích doanh thu theo khoa/tháng
  //
  // TECHNICAL: Có yêu cầu/ràng buộc kỹ thuật gì?
  //   VD: Dữ liệu nhạy cảm phải được ẩn danh trước khi đưa vào Data Warehouse. 

  title varchar(255) [not null]
  description text [not null]

  priority varchar(30) [not null, default: 'MEDIUM',
    note: 'HIGH, MEDIUM, LOW'
  ]

  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    project_id
  }
}


// ============================================================
// 5. ANALYTICAL REQUIREMENTS
// ============================================================

// requirements
// = "Người dùng/business yêu cầu gì?"

// analytical_requirements
// = "Cụ thể cần phân tích dữ liệu như thế nào để đáp ứng
//    requirement đó?"


// Ví dụ:
// Requirement:
// "Phân tích doanh thu theo khoa."

//         ↓

// Analytical Requirement:

// Metric:
// Revenue

// Dimension:
// Department

// Time:
// Month

// Aggregation:
// SUM

//         ↓

// Data Model:

// Fact_Revenue
// Dim_Department
// Dim_Date

Table analytical_requirements {
  id uuid [pk]
  requirement_id uuid [not null]

  metric varchar(255)
  dimension varchar(255)
  time_granularity varchar(50)
  aggregation_method varchar(50)
  grain text

  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    requirement_id
  }
}


// ============================================================
// 6. DATA SOURCES
// ============================================================

Table data_sources {
  id uuid [pk]
  project_id uuid [not null]
  name varchar(255) [not null]
  type varchar(50) [not null, note: 'CSV (MVP sẽ chỉ dùng dạng file này), EXCEL (XLSX), JSON, SQL, TEXT (TXT, MD, DOCX, PDF) etc.']
  description text
  location text [not null]
  schema_metadata jsonb [
    note: 'Structured metadata extracted from the source, including tables, columns, relationships, and other inferred schema information'
  ]
  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    project_id
    type
  }
}

// VD schema_metadata:
// {
//   "tables": [
//     {
//       "name": "patients",
//       "columns": [
//         {
//           "name": "patient_id",
//           "data_type": "integer",
//           "primary_key": true
//         },
//         {
//           "name": "department_id",
//           "data_type": "integer",
//           "foreign_key": {
//             "references": "departments.department_id"
//           }
//         }
//       ]
//     }
//   ],
//   "relationships": [
//     {
//       "from": "patients.department_id",
//       "to": "departments.department_id",
//       "type": "many_to_one"
//     }
//   ]
// }


// ============================================================
// 9. AGENT COMMUNICATION
// ============================================================

Table project_sessions {
  id uuid [pk]
  project_id uuid [not null]
  user_id uuid [not null]

  title varchar(255)

  status varchar(30) [not null, default: 'ACTIVE',
    note: 'ACTIVE, COMPLETED, ARCHIVED'
  ]

  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    project_id
    user_id
    status
  }
}

Ref: project_sessions.user_id > users.id

Table session_events {
  id uuid [pk]
  session_id uuid [not null]

  role varchar(30) [not null,
    note: 'USER, AGENT, TOOL'
  ]

  // USER     + MESSAGE       → user gửi message
  // AGENT    + MESSAGE       → agent trả lời
  // AGENT    + QUESTION      → agent hỏi (có tác dụng pause workflow)
  // USER     + ANSWER        → user trả lời câu hỏi của agent (user trả lời xong mới có thể tiếp tục workflow)

  // AGENT    + AGENT_CALL    → agent gọi agent khác
  // AGENT    + AGENT_RESULT  → agent trả kết quả

  // AGENT    + TOOL_CALL     → agent gọi tool
  // TOOL     + TOOL_RESULT   → tool trả kết quả

  type varchar(50) [not null,
    note: 'MESSAGE, QUESTION, ANSWER, AGENT_CALL, AGENT_RESULT, TOOL_CALL, TOOL_RESULT'
  ]

  content text
  metadata jsonb
  // MESSAGE, role USER: metadata = null
  // MESSAGE, role AGENT: metadata = { "model": "..." }

  // AGENT_CALL: metadata = {
  //   "caller_agent": "...",
  //   "target_agent": "...",
  //   "input": {...}
  // }

  // AGENT_RESULT, status SUCCESS: metadata = {
  //   "session_event_id": "...",
  //   "agent": "...",
  //   "status": "SUCCESS",
  //   "output": {...},
  //   "llm": {
  //     "provider": "...",
  //     "model": "...",
  //     "input_tokens": 0,
  //     "output_tokens": 0,
  //     "total_tokens": 0,
  //     "temperature": 1.5,
  //     "latency_ms": 0,
  //     "finish_reason": "..."
  //   }
  // }

  // AGENT_RESULT, status FAILED: metadata = {
  //   "session_event_id": "...",
  //   "agent": "...",
  //   "status": "FAILED",
  //   "error": "..."
  // }

  // AGENT_RESULT, status CANCELLED: metadata = {
  //   "session_event_id": "...",
  //   "agent": "...",
  //   "status": "CANCELLED",
  //   "error": "Agent execution was cancelled"
  // }

  // TOOL_CALL: metadata = {
  //   "agent": "...",
  //   "tool": "...",
  //   "arguments": {...}
  // }

  // TOOL_RESULT, status SUCCESS: metadata = {
  //   "session_event_id": "...",
  //   "tool": "...",
  //   "status": "SUCCESS",
  //   "result": {...}
  // }

  // TOOL_RESULT, status FAILED: metadata = {
  //   "session_event_id": "...",
  //   "tool": "...",
  //   "status": "FAILED",
  //   "error": "..."
  // }

  created_at timestamp [not null]

  indexes {
    session_id
    created_at
  }
}

Ref: project_sessions.project_id > projects.id
Ref: session_events.session_id > project_sessions.id


// ============================================================
// 14. DATA MODEL
// ============================================================
Table data_models {
  id uuid [pk]
  project_id uuid [not null]
  dbml text [not null]
  revision integer [not null, default: 1]
  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    project_id
  }
}

Table data_model_changes {
  id uuid [pk]
  data_model_id uuid [not null]
  base_revision integer [not null]
  proposed_dbml text [not null]

  status varchar(30) [not null, default: 'PROPOSED',
    note: 'PROPOSED, ACCEPTED, REJECTED, CONFLICTED'
  ]
  // PROPOSED (đề xuất): chưa chấp nhận hay từ chối -> giữ bảng cũ
  // ACCEPTED: chấp nhận thay đổi -> giữ bảng mới
  // REJECTED: từ chối thay đổi -> giữ bảng cũ

  user_id uuid [not null]

  created_at timestamp [not null]
  updated_at timestamp [not null]

  // PostgreSQL partial unique index:
  // UNIQUE (data_model_id, user_id) WHERE status = 'PROPOSED'
}

Ref: data_model_changes.data_model_id > data_models.id
Ref: data_model_changes.user_id > users.id

// Happy case 1 — Một người chỉnh sửa DBML: Người dùng lấy DBML hiện tại kèm revision, chỉnh sửa và gửi lên; hệ thống kiểm tra revision vẫn khớp với DB hiện tại thì cập nhật DBML và tăng revision lên 1.

// Happy case 2 — Nhiều người cùng mở một DBML nhưng chỉ một người lưu trước: Người lưu trước được cập nhật bình thường; người lưu sau gửi lên revision cũ nên hệ thống phát hiện DBML đã thay đổi và yêu cầu người dùng tải lại hoặc xem thay đổi trước khi tiếp tục.

// Happy case 3 — Agent tạo thay đổi DBML: Agent không sửa trực tiếp DBML hiện tại mà tạo data_model_change chứa DBML đề xuất và base_revision là revision tại thời điểm Agent bắt đầu xử lý; người dùng có thể xem và Accept/Reject.

// Happy case 4 — User Accept thay đổi của Agent: Hệ thống kiểm tra base_revision của change có bằng revision hiện tại hay không; nếu khớp thì áp dụng DBML mới, tăng revision và đánh dấu change là ACCEPTED.

// Edge case 1 — User Accept một change đã cũ: Nếu base_revision của change khác revision hiện tại thì không được áp dụng, change chuyển sang CONFLICTED và người dùng phải xem lại hoặc tạo lại thay đổi dựa trên DBML mới.

// Edge case 2 — Hai người cùng Accept hai thay đổi dựa trên cùng một revision: Database sử dụng transaction và optimistic locking để chỉ một thao tác được cập nhật thành công; thao tác còn lại phát hiện revision đã thay đổi và chuyển thành conflict.

// Edge case 3 — Hai thay đổi không thực sự xung đột: Hệ thống có thể cho phép tạo proposal mới dựa trên DBML hiện tại hoặc sau này hỗ trợ merge DBML; trong MVP nên yêu cầu người dùng xem lại thay đổi thay vì tự động merge.

// Edge case 4 — Agent đang xử lý thì người khác thay đổi DBML: Agent vẫn hoàn thành và tạo data_model_change dựa trên revision cũ, nhưng khi Apply hệ thống phát hiện revision không còn khớp và không cho ghi đè DBML hiện tại.

// Edge case 5 — Người dùng mở DBML quá lâu rồi mới lưu: Khi lưu, hệ thống kiểm tra revision; nếu revision đã thay đổi thì từ chối ghi đè và yêu cầu người dùng cập nhật DBML trước khi lưu.

// Edge case 6 — Người dùng Reject thay đổi: Chỉ đánh dấu data_model_change là REJECTED, DBML hiện tại và revision không thay đổi.

// Edge case 7 — Agent tạo nhiều thay đổi liên tiếp: Mỗi người dùng chỉ được có một proposal PROPOSED trên cùng một Data Model. Phải Accept, Reject hoặc kết thúc proposal cũ do conflict trước khi tạo proposal mới; hệ thống không tự thay thế proposal cũ.

// Edge case 8 — Hai người cùng thao tác đúng một thời điểm: Database transaction + optimistic locking đảm bảo chỉ một request được cập nhật revision thành công, request còn lại nhận conflict thay vì ghi đè dữ liệu.

// ============================================================
// 18. RELATIONSHIPS
// ============================================================

// User / Project
Ref: projects.user_id > users.id

// Requirement hierarchy
Ref: requirements.project_id > projects.id

// Analytical Requirements
Ref: analytical_requirements.requirement_id > requirements.id

// Data Sources
Ref: data_sources.project_id > projects.id

// Data Model
Ref: data_models.project_id > projects.id
```
