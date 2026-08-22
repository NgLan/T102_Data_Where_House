# Kế hoạch refactor Project Init và Source Data Analysis

## Mục tiêu

- Refactor Project Init theo SRP, DRY, FSD, naming, i18n và giới hạn kích thước trong coding guidelines.
- Tách upload CSV nhẹ khỏi full analysis; chỉ chạy DuckDB profiling, logical type inference và LLM classifier sau action **Lưu & Phân tích**.
- Giữ Raw Requirement editable, hiển thị Markdown đẹp; Structured Requirements và CSV schema là kết quả read-only.
- Dùng generated OpenAPI SDK, thư viện được duy trì và shadcn primitives thay cho implementation thủ công.

## Backend và API

- Upload chỉ validate extension, size, tổng tối đa 20 source, encoding/header và khả năng đọc; lưu source với `schema_metadata=None` và trạng thái `PENDING`.
- Đổi upload counter thành `total_files_uploaded`; thêm `analysis_status`, `is_unique_candidate` và `is_key_candidate` vào response metadata.
- Khi Analyze, chạy `DuckDB typed/raw parsing → profiler → rule inference → ColumnTypeClassifier khi confidence thấp → persist schema → RequirementAgent`.
- Giữ một `data_type` cuối cùng, không thêm `semantic_type`; classifier dùng structured enum, sample giới hạn và PII Guard.
- Xóa public create/update Structured Requirement, giữ read API; regenerate Frontend SDK từ OpenAPI.

## Frontend

- Dùng TanStack Query cho project/source/preview/status và mutation; React Hook Form + generated Zod schema cho form.
- **Lưu & Phân tích** lưu form, gọi `reanalyzeProject`, refetch kết quả và ở lại trang; nút **Tiếp tục** riêng chỉ mở khi analysis current.
- Chuyển requirement document upload vào Project Details; dùng `react-dropzone`, `react-markdown`, `remark-gfm` và Tailwind Typography.
- Requirements table read-only, ba cột sortable với default HIGH → MEDIUM → LOW, BUSINESS → ANALYTICAL → TECHNICAL, title A–Z.
- Source list là collapsible dọc; expanded body hiển thị bảng Column/Data Type/Properties read-only và preview đọc lười.
- Dùng shadcn `collapsible`, `table`, `tabs`, `empty`; chuẩn hóa hover/cursor, skeleton, empty/error state và i18n VI/EN.

## Kiểm thử chấp nhận

- Backend: identifier/date/category/free-text rules, ambiguous classifier, invalid structured output, upload nhẹ, giới hạn tổng source và revision conflict.
- API: pending/ready source, renamed upload counter, candidate properties, read-only Requirements contract và OpenAPI generated SDK.
- Frontend: Markdown an toàn, dropzone click/drag, sorting/read-only table, collapsible/delete độc lập, Save → Analyze → refetch và Continue gating.
- Chạy Ruff, Pytest, export OpenAPI, `npm run api:generate`, `npm run lint`, `npm test`, `npm run build`.

## Giả định đã chốt

- Source preview được giữ trong expanded card; Project Init không chỉnh metadata cột dù API tương thích có thể được giữ cho consumer khác.
- Không tạo SourceDataAgent, không thêm `semantic_type`, không sửa generated code thủ công và không cần migration cột CSDL.
- Các thay đổi i18n tiếng Việt hiện có trong worktree phải được giữ nguyên.
