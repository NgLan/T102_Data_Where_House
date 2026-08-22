# Kế hoạch refactor Modeling Dashboard

## 1. Mục tiêu và phạm vi

Tài liệu này là kế hoạch refactor, không phải phần triển khai. Phạm vi audit chính là toàn bộ `frontend/src/features/modeling-dashboard/`; các feature `project-init`, `project-management`, thư mục `frontend/src/common/components/ui/`, generated API và API Backend liên quan chỉ được đọc để đối chiếu kiến trúc và xác định dependency.

Mục tiêu sau refactor:

- Tuân thủ `TECHNICAL_CODING_GUIDELINES.md`, đặc biệt SRP, DRY, giới hạn 120 dòng logic/file và 25 dòng logic/function.
- Giữ `ModelingDashboardScreen.tsx` ở root feature và chỉ export public API qua `index.ts`.
- Thay AI Insights demo/floating widget bằng Validation Engine deterministic, chạy trên DBML draft mới nhất và không gọi LLM.
- Hiển thị lỗi/cảnh báo trực tiếp trên từng table node của ERD: `ERROR` màu đỏ, `WARNING` màu vàng, hover/focus xem chi tiết.
- Mặc định chia màn hình thành DBML → ERD → Agent; tự đóng “Chi tiết bảng” khi vào trang.
- Cho phép Agent dock bên phải, chuyển xuống dưới “Chi tiết bảng”, hoặc đóng; các panel resize được.
- Agent có nhiều session, lịch sử bền vững, clarification question, timeline sự kiện và trạng thái đang chạy tương tự extension IDE, nhưng không hiển thị chain-of-thought nội bộ.
- Chỉ dùng generated API types/client; không tự định nghĩa lại DTO Backend.
- Dùng component có sẵn trong `common/components/ui`; component phổ biến còn thiếu thì cài từ shadcn thay vì tự dựng.

## 2. Kết luận audit hiện trạng

Kết luận: module **chưa tuân thủ đầy đủ guideline** và **chưa đáp ứng yêu cầu sản phẩm mới**.

Điểm đang làm đúng:

- Public screen và `index.ts` đặt đúng vị trí.
- Không có import chéo sang feature khác.
- Các API hiện có đều đi qua generated SDK và `requireApiData`.
- Đã dùng thư viện phù hợp cho DBML (`@dbml/core`), graph (`@xyflow/react`), layout (`elkjs`), diff (`diff`) và validation form (`zod`).
- Phần lớn control cơ bản dùng `Button`, `Input`, `Textarea`, `NativeSelect`, `Tooltip`, `ConfirmationDialog`, `Skeleton` trong common UI.
- Namespace i18n đã được đăng ký cho cả VI/EN.
- Kiểm tra hiện trạng ngày 2026-08-22: ESLint pass; 18 test file với 56 test đều pass.

Điểm chưa đạt:

- Feature có 101 file/7.101 dòng; cấu trúc bị dồn dưới umbrella folder `modeling-workspace`, trong khi các capability nghiệp vụ đã đủ lớn để trở thành sub-feature độc lập.
- Có 14 source file vượt 120 dòng logic; có ít nhất 49 function/component production có body dài hơn 25 dòng theo phép đo line span và cần review/tách theo trách nhiệm.
- `ModelingWorkspace.tsx` đang đồng thời điều phối snapshot, selection, layout, inspector, chat, proposal, notice và shortcut.
- `DataModelInspector.tsx` nhận `chatSlot`, khiến inspector sở hữu cả layout của một capability không liên quan.
- `use-document-synchronization.ts` trộn reducer orchestration, debounce parser, refs chống race, serialize và error state.
- Validation local, validation Backend và rule relationship/column đang chồng lấn nguồn sự thật.
- `use-resizable-dbml-editor.ts` và `use-resizable-inspector.ts` lặp lại gần như cùng một cơ chế resize tự viết.
- `DbmlDiffHeader.tsx` tự dùng `<button>` dù common `Button` đã tồn tại.
- Một số empty/error/status UI tự dựng lại thay vì dùng `Empty`, `Badge`, `Alert`, `ScrollArea` hoặc component shadcn tương ứng.
- Naming acronym không nhất quán (`AIInsights*`, `AiChat*`, `DBML*`, `ERD*`, trong khi convention chung của repo dùng `Api*`, `Pii*`, `Dbml*`).
- Tên `ai-insights` không còn đúng domain; dữ liệu thực tế là Validation Engine deterministic.
- `UpdateDataModelButton` có thể create/generate/regenerate nên tên hiện tại không mô tả đúng trách nhiệm.
- `create-demo-ai-insights.ts` và test của nó là dead/demo code, không được dùng ở runtime.

### 2.1. Các file chắc chắn vượt giới hạn 120 dòng logic

| File | Dòng logic đo được | Vấn đề trách nhiệm chính |
|---|---:|---|
| `modeling-workspace/components/ModelingWorkspace.tsx` | 219 | Orchestration, layout, notice, proposal và chat |
| `dbml-editor/hooks/use-document-synchronization.ts` | 191 | Parse, debounce, reducer sync, serialization và race control |
| `model-document/reducers/data-model-editor-reducer.ts` | 189 | Action contract và toàn bộ mutation handlers |
| `model-document/utils/data-model-cascade.ts` | 188 | Cascade table và column trong cùng file |
| `model-inspector/.../ColumnEditorRow.tsx` | 184 | Row UI, state mở rộng, impact analysis và confirm dialog |
| `model-document/utils/column-constraints.ts` | 163 | Effective constraint, impact và reference lookup |
| `ai-chat/components/AiChatPanel.tsx` | 162 | Header, empty state, timeline, bubble, composer và error mapping |
| `model-document/utils/reference-validation.ts` | 157 | Nhiều validation rule độc lập |
| `relationship-inspector/ForeignKeyField.tsx` | 156 | Candidate query, tạo/xóa FK và presentation |
| `relationship-inspector/RelationshipInspector.tsx` | 154 | Endpoint, cardinality, referential action và delete flow |
| `erd-canvas/components/ERDCanvas.tsx` | 137 | Toolbar, graph interaction, mount fallback và empty state |
| `erd-canvas/hooks/use-erd-canvas.ts` | 130 | Graph sync, persistence, search, layout và instance state |
| `hooks/use-data-model-snapshot.ts` | 125 | Load, save, generate và notifications |
| `column-settings/ColumnSettings.tsx` | 121 | Tất cả column settings và nhiều confirmation flow |

### 2.2. Vi phạm DRY và nguồn sự thật

- Logic nhận diện endpoint/reference lặp tại `reference-validation.ts`, `data-model-cascade.ts`, `column-constraints.ts`, `erd-graph-mapper.ts` và `ForeignKeyField.tsx`.
- Cách hiển thị PK/FK lặp tại `ERDTableNode.tsx` và `ColumnEditorRow.tsx`, gồm cả aria-label hardcode.
- Hai resize hook tự quản lý pointer capture, min/max, keyboard step và width state.
- Frontend tự đánh giá nhiều semantic rule trong khi Backend đã có `DbmlValidationEngine`; hai phía có thể cho kết quả khác nhau.
- `parseDbml()` gọi parser theo hai đường liên tiếp; cần xác minh và giữ đúng một parse path nếu API `@dbml/core` cho phép.
- `DbmlDocument.sourceModel: unknown` làm raw model thư viện đi vào application/view state thay vì được cô lập hoàn toàn sau adapter.

### 2.3. Lỗi i18n, naming và contract đã phát hiện

- `use-ai-insights.ts` hardcode hai thông báo tiếng Việt.
- `use-ai-chat.ts` hardcode `AWAITING_REVIEW_NOTE` bằng tiếng Việt.
- `ERDTableNode.tsx` và `ColumnEditorRow.tsx` hardcode aria-label “Primary Key”/“Foreign Key”.
- `AIInsightsPanel.tsx` gọi `TXT_LOADING` trong namespace `ai-insights` nhưng key nằm ở `modeling-workspace`; `BTN_RETRY` dùng fallback hardcode “Thử lại”.
- `DataTypeParameters.tsx` đọc key `DATA_TYPE_*` từ `model-inspector`, nhưng các key này hiện nằm ở `modeling-workspace`.
- `schema.ts` phát mã `MSG_MSG_INVALID_DATA_TYPE_PARAMETERS`, trong khi translation đúng là `MSG_INVALID_DATA_TYPE_PARAMETERS`.
- Nội dung `ai-chat.json` nói Agent “lưu ngay thành revision mới”, trái với implementation tạo proposal chờ Human-in-the-Loop.
- `modeling-dashboard.json` hiện không được screen sử dụng.
- `AIInsightSeverity` có `info`, trong khi generated Backend contract chỉ có `WARNING | ERROR`.
- Mapping insight làm mất `code` và `column_name`, nên không đủ dữ liệu để gắn cảnh báo chính xác lên table/column.

### 2.4. Khoảng trống chức năng/API

- `useAiInsights` chỉ gọi `GET /projects/{project_id}/data-model/validation-issues` lúc mount/reload.
- Endpoint hiện tại chỉ validate snapshot đã lưu; nó không nhận DBML draft. Vì vậy FE không thể đúng yêu cầu “phân tích mỗi khi nội dung bảng thay đổi” nếu không bổ sung contract.
- Response chỉ có `table_name`/`column_name`; thiếu `schema_name` hoặc locator ổn định, nên có thể map sai khi hai schema có table trùng tên.
- Chat hiện là state trong memory, mất khi reload, chỉ có một luồng, không có session list/history/event stream/clarification/cancel.
- Backend đã có domain/repository cho project session event nhưng chưa có Presentation API trong OpenAPI/generated SDK.
- Manual save ở dự án chưa có snapshot đang mâu thuẫn: `canSave` cho phép, comment nói cho phép, nhưng `useSnapshotSaver` trả `null` khi `snapshot` chưa tồn tại và request DTO bắt buộc `data_model_id/base_revision`. Cần chốt UX/API thay vì giữ silent no-op.
- ID table/column dựa trên source index (`source-table-{index}`) không ổn định khi người dùng reorder DBML, ảnh hưởng selection, canvas layout và mapping validation.
- Search với query rỗng có thể match table đầu tiên; auto-layout error chưa có UI error flow.

## 3. Quyết định kiến trúc cần chốt trước khi refactor FE

### 3.1. Validation draft là contract bắt buộc

Không autosave DBML chỉ để gọi endpoint validation hiện tại. Cần bổ sung một endpoint read-only, deterministic, ví dụ:

```text
POST /api/v1/projects/{project_id}/data-model/validate
body: { dbml: string }
response: DataModelValidationIssueResponse[]
```

Response nên có tối thiểu:

- `code`: generated enum.
- `severity`: `WARNING | ERROR`.
- `schema_name`, `table_name`, `column_name` hoặc một `location` typed, không map chỉ bằng table name.
- `params` typed nếu câu dịch cần dữ liệu động.
- Không yêu cầu title/description tiếng Anh làm nguồn UI; FE dịch theo `code` và params qua i18n.

Endpoint phải chỉ chạy parser + Validation Engine, không gọi LLM, không ghi Data Model và không tăng revision.

Sau khi Backend cập nhật OpenAPI, chạy `npm run api:generate`; FE chỉ import generated operation/type.

### 3.2. Agent session/event API là contract bắt buộc

Để đáp ứng session và history thật, cần public API thay vì localStorage/mock:

- List/create/rename/archive agent sessions theo project.
- Đọc event history có cursor pagination.
- Gửi message/answer vào một session.
- Stream event qua SSE hoặc WebSocket, hỗ trợ reconnect từ event ID/cursor.
- Cancel/retry run nếu Backend hỗ trợ.
- Event contract typed tối thiểu: user message, assistant message, status summary, tool started/completed/failed, clarification question, answer, proposal created, error, run completed/cancelled.

UI chỉ hiển thị status summary và sự kiện quan sát được; không yêu cầu hoặc hiển thị private chain-of-thought. Proposal vẫn phải đi qua flow Accept/Reject hiện tại.

### 3.3. Chính sách lưu model đầu tiên

Chọn đúng một trong hai hướng và phản ánh nhất quán trong API/UI/test:

1. Model đầu tiên chỉ được tạo qua Generate workflow: tắt Save khi chưa có snapshot và sửa toàn bộ copy/comment.
2. Cho phép manual create: bổ sung generated create/upsert contract không cần optimistic revision ban đầu.

Không giữ trạng thái nút Save khả dụng nhưng request silent no-op.

## 4. Cấu trúc thư mục đích

Đưa các capability lớn lên thành sub-feature ngang cấp, tương tự cách `project-init` và `project-management` phân nhóm theo nghiệp vụ:

```text
modeling-dashboard/
├── ModelingDashboardScreen.tsx
├── index.ts
├── constants/
│   └── modeling-dashboard-query-keys.ts
├── workspace/
│   ├── components/
│   │   ├── ModelingWorkspace.tsx
│   │   ├── ModelingWorkspaceHeader.tsx
│   │   ├── ModelingWorkspaceNotices.tsx
│   │   └── ModelingWorkspaceSkeleton.tsx
│   ├── hooks/
│   │   ├── use-modeling-workspace.ts
│   │   ├── use-workspace-layout.ts
│   │   └── use-workspace-shortcuts.ts
│   └── types/
│       └── workspace-layout-types.ts
├── data-model-document/
│   ├── dbml/
│   ├── reducers/
│   ├── types/
│   └── utils/
├── data-model-snapshot/
│   ├── hooks/
│   └── services/
├── dbml-editor/
├── erd-canvas/
├── model-inspector/
├── validation/
├── agent-chat/
└── proposal-review/
```

Nguyên tắc:

- `workspace` chỉ ghép layout/capability, không chứa rule của document, validation hoặc agent.
- `data-model-document` là nguồn state draft và mutation thuần.
- `data-model-snapshot` chỉ quản lý persistence/revision/generation.
- `validation` sở hữu API draft validation, query state, issue mapping và panel.
- `agent-chat` sở hữu sessions, event timeline, composer và stream lifecycle.
- `model-inspector` không nhận `chatSlot`.
- Không tạo barrel nội bộ tràn lan; `index.ts` root vẫn chỉ export screen công khai.
- Chuẩn hóa acronym theo convention repo: `Ai*`, `Api*`, `Dbml*`, `Erd*`; hook tương ứng `useAi*`, `useErd*`.

## 5. Kế hoạch triển khai theo phase

### Phase 0 — Characterization và khóa contract

- [ ] Thêm test mô tả hành vi hiện tại cho load/save/conflict/generate/proposal trước khi move file.
- [ ] Thêm test tái hiện manual initial save silent no-op và chốt policy ở mục 3.3.
- [ ] Chốt request/response draft validation, locator table/column và error behavior.
- [ ] Chốt Agent session/event state machine, pagination, stream reconnect và clarification flow.
- [ ] Generate SDK từ OpenAPI; tuyệt đối không viết DTO request/response trong feature.
- [ ] Ghi rõ feature flag hoặc trạng thái disabled nếu Agent API chưa sẵn sàng; không dùng demo data làm fallback production.

Điều kiện hoàn thành: contract được review, generated operations/types tồn tại và characterization tests pass.

### Phase 1 — Dọn naming, dead code và i18n

- [ ] Đổi `ai-insights` thành `validation`; đổi `AIInsightsPanel`, `AIInsightCard`, `useAiInsights` và view model theo đúng Validation domain.
- [ ] Xóa `create-demo-ai-insights.ts`, test và các translation demo không còn dùng.
- [ ] Đổi `ai-chat` thành `agent-chat`; tên component/hook phản ánh session/event thay vì one-shot proposal.
- [ ] Đổi các tên acronym còn lại theo một convention duy nhất, cập nhật test filename bám đúng source.
- [ ] Đổi `UpdateDataModelButton` thành tên đúng hành vi đã chốt, ví dụ `GenerateDataModelButton`.
- [ ] Chuyển toàn bộ hardcoded UI/aria/error text sang namespace đúng.
- [ ] Sửa `MSG_MSG_INVALID_DATA_TYPE_PARAMETERS`.
- [ ] Sửa copy Agent để mô tả đúng proposal chờ duyệt.
- [ ] Xóa key/namespace không dùng hoặc đưa screen title/subtitle vào UI thực tế.
- [ ] Thêm test exhaustiveness VI/EN cho toàn bộ validation issue code và agent event label.

Điều kiện hoàn thành: không còn UI text hardcode, không còn demo runtime code, key VI/EN đồng bộ và naming nhất quán.

### Phase 2 — Tách workspace shell và layout dockable

- [ ] Đặt `isInspectorOpen` mặc định `false`; không tự mở inspector khi load trang.
- [ ] Tạo state `agentPlacement: "right" | "below-inspector" | "hidden"` trong `use-workspace-layout.ts`.
- [ ] Mode `right`: DBML → ERD → Agent; nếu người dùng mở inspector thì inspector và Agent là hai dock độc lập.
- [ ] Mode `below-inspector`: DBML → ERD → right dock; nửa trên inspector, nửa dưới Agent.
- [ ] Nếu inspector đóng khi đang ở `below-inspector`, Agent chiếm right dock thay vì biến mất.
- [ ] Thêm action Move below details / Move right / Close trong Agent header; thêm action mở lại Agent ở workspace header.
- [ ] Dùng shadcn `ResizablePanelGroup`, `ResizablePanel`, `ResizableHandle` cho cả chia ngang và chia dọc.
- [ ] Xóa `use-resizable-dbml-editor.ts`, `use-resizable-inspector.ts` và pointer/keyboard resize code trùng lặp.
- [ ] Dùng `Sheet`/`Tabs` cho breakpoint nhỏ nếu resizable multi-column không khả dụng; không dùng fixed overlay che nội dung chính.
- [ ] Tách notice, skeleton và proposal region khỏi `ModelingWorkspace.tsx` để file chỉ còn orchestration cấp cao.
- [ ] Chỉ persist `agentPlacement`/panel size nếu cần; trạng thái inspector lúc vào trang vẫn phải đóng theo yêu cầu.

Common UI:

- Dùng ngay `Button`, `Tooltip`, `Tabs`, `Collapsible`, `Badge`, `Empty`, `Skeleton`, `Separator` đã có.
- Cài từ shadcn các component còn thiếu thực sự cần: `resizable`, `scroll-area`, `sheet`, `alert`, `card`.
- Không tạo primitive resize/card/alert/scroll mới trong feature.

Điều kiện hoàn thành: ba mode Agent hoạt động bằng mouse và keyboard, layout không overlay ERD, inspector mặc định đóng, responsive có fallback rõ ràng.

### Phase 3 — Validation Engine trên draft và cảnh báo ERD

- [ ] Tạo `validation/services/data-model-validation-api.ts` gọi generated draft-validation operation.
- [ ] Tạo `use-data-model-validation.ts` nhận DBML draft hiện tại, debounce hợp lý (đề xuất 400–600 ms), hủy request cũ và bỏ response stale.
- [ ] Mỗi draft mới nhất sau khi người dùng ngừng gõ phải được validate; không chờ Save và không gọi LLM.
- [ ] Khi DBML đang sai cú pháp, vẫn gửi raw DBML cho engine để nhận syntax issue; giữ canvas ở last valid document nhưng không gắn issue cũ như kết quả mới.
- [ ] Phân biệt `isValidating`, `isStale`, `isError`, `issues`; có retry và trạng thái offline/API error thân thiện.
- [ ] Không trộn API failure với validation `ERROR`: một bên là lỗi hệ thống, một bên là kết quả nghiệp vụ.
- [ ] Giữ generated severity/code; không tạo thêm `info` nếu Backend không có.
- [ ] Tạo selector thuần `group-validation-issues-by-table.ts` dùng locator schema/table; aggregate `ERROR` ưu tiên hơn `WARNING`.
- [ ] Mở rộng `ErdTableNodeData` bằng validation view model tối thiểu, không truyền toàn bộ hook state.
- [ ] Tách `ErdTableHeader.tsx`; dùng đỏ cho error, vàng cho warning, trạng thái bình thường giữ theme mặc định.
- [ ] Dùng common `Tooltip` cho icon dấu chấm than; tooltip focus được bằng keyboard và liệt kê code/title/column đã dịch.
- [ ] Với nhiều issue, header hiển thị severity cao nhất và badge số lượng; panel Validation cho phép lọc table và focus node tương ứng.
- [ ] Thay floating Sparkles/Bot của AI Insights bằng launcher Validation có icon deterministic (`ShieldCheck`/`CircleAlert`), count và trạng thái đang validate.
- [ ] Khi chọn issue trong panel, focus đúng table qua một command chung của ERD; không copy logic `setCenter`.
- [ ] Tách local editor validation thành hai lớp rõ ràng:
  - syntax/shape tức thời phục vụ input và khả năng serialize;
  - Validation Engine là nguồn sự thật cho quality/business issues.
- [ ] Loại các semantic rule FE trùng Backend hoặc ghi rõ rule nào bắt buộc giữ local để bảo vệ editor invariant.

Điều kiện hoàn thành: sửa nội dung DBML hoặc inspector làm validation tự chạy trên draft; warning/error xuất hiện đúng table; response cũ không ghi đè response mới; không có request LLM.

### Phase 4 — Agent nhiều session và event timeline

- [ ] Tách `AgentPanel`, `AgentSessionList`, `AgentSessionHeader`, `AgentEventTimeline`, `AgentComposer`, `AgentEmptyState` và `AgentRunStatus`.
- [ ] Dùng TanStack Query cho session list/history; định nghĩa query keys tập trung trong `modeling-dashboard-query-keys.ts`.
- [ ] Tạo session mới, chuyển session, rename/archive nếu contract hỗ trợ; session đang chọn lấy từ route/search param hoặc state ổn định.
- [ ] Lịch sử phải tải lại được sau refresh và hỗ trợ load older events bằng cursor.
- [ ] Stream event mới với cleanup/reconnect; deduplicate theo event ID và giữ đúng thứ tự server.
- [ ] Hiển thị event card theo loại: message, status, tool, clarification, proposal, error, completion.
- [ ] `thinking/running` hiển thị status summary và tool events; không render reasoning token/chain-of-thought.
- [ ] Clarification question có UI trả lời rõ ràng; trong trạng thái chờ người dùng không hiển thị spinner vô hạn.
- [ ] Composer hỗ trợ Enter gửi, Shift+Enter xuống dòng, disabled reason, retry và cancel khi có contract.
- [ ] Message body dùng `react-markdown` + `remark-gfm` đã có trong dự án; sanitize/giới hạn link và code rendering theo policy chung.
- [ ] Proposal event mở `ProposalReview` hiện tại; Accept/Reject cập nhật cả proposal cache, snapshot, validation và event timeline.
- [ ] Không giữ `handleApiError(...).errorCode` làm message text; map lỗi qua notification/errors i18n hoặc typed error event.
- [ ] Xóa `changedTables` local nếu server không cung cấp; nếu cần thì đưa field này vào generated event metadata.

Điều kiện hoàn thành: tạo và chuyển nhiều session, reload vẫn thấy history, clarification round-trip được, event stream reconnect không nhân đôi event, proposal vẫn có HITL.

### Phase 5 — Refactor SRP/DRY trong document, inspector và canvas

- [ ] Tách `data-model-cascade.ts` thành table cascade, column cascade và endpoint matching utility có tên nghiệp vụ cụ thể.
- [ ] Tách `column-constraints.ts` thành effective constraints, data-type change impact và column reference query.
- [ ] Thu gọn reducer: action types riêng; mỗi nhóm table/column/reference có mutation thuần; reducer chỉ dispatch.
- [ ] Tách `use-document-synchronization.ts` thành draft state, debounced parser và document serialization; giữ race test.
- [ ] Cô lập raw `@dbml/core` model trong adapter; không để `unknown` tùy tiện lan qua view model.
- [ ] Xác minh một parse path duy nhất của `@dbml/core`; không hy sinh round-trip metadata.
- [ ] Tạo table locator/identity strategy ổn định qua reorder/reparse; layout storage, selection và validation cùng dùng một contract locator.
- [ ] Tách `ColumnEditorRow` thành row summary, data-type impact controller và settings body.
- [ ] Tách `RelationshipInspector` thành endpoint fields, cardinality field và referential action section.
- [ ] Tách `ForeignKeyField` thành candidate selector và existing-reference list; factory tạo reference là pure function dùng chung với ERD connect.
- [ ] Tách `ErdCanvasToolbar`, `ErdCanvasViewport`, `ErdEmptyState`; hook canvas không sở hữu cả search, auto-layout và persistence nếu chúng thay đổi độc lập.
- [ ] Dùng một component `ColumnKeyIndicator` cho PK/FK ở inspector và ERD.
- [ ] Search query rỗng không focus table; thêm no-result feedback.
- [ ] Bắt lỗi auto-layout thành typed UI state và retry action.
- [ ] Sau mỗi lần tách, giữ file ≤120 dòng logic và function ≤25 dòng logic; dùng input object nếu function cần hơn ba tham số.

Điều kiện hoàn thành: không còn file trong danh sách mục 2.1 vượt ngưỡng; endpoint/reference logic có một nguồn; adapter boundary rõ; hành vi round-trip không đổi.

### Phase 6 — Chuẩn hóa UI, accessibility và trạng thái

- [ ] Thay raw `<button>` trong diff header bằng common `Button`.
- [ ] Dùng common/shadcn `Empty`, `Alert`, `Badge`, `ScrollArea`, `Card` cho pattern chuẩn; không thay các domain component thực sự riêng như ERD table node bằng generic card một cách máy móc.
- [ ] Mọi clickable element có cursor/hover/focus-visible; icon-only action có localized aria-label và tooltip.
- [ ] Tooltip validation dùng được bằng hover lẫn keyboard focus; màu không phải tín hiệu duy nhất.
- [ ] Initial fetch dùng skeleton; list session/history có empty, error, retry và loading-more state.
- [ ] Kiểm tra contrast cho đỏ/vàng trên light/dark theme.
- [ ] Thêm aria-live phù hợp cho validation count và agent run status, tránh announce mọi token/event quá dày.
- [ ] Chuẩn hóa dynamic class bằng `cn()` thay vì template string phức tạp.

## 6. Ma trận test bắt buộc

### Unit test

- Validation debounce, abort, stale-response guard, grouping theo schema/table và severity aggregate.
- Workspace layout reducer cho `right`, `below-inspector`, `hidden`, inspector closed fallback.
- Session event reducer/dedup/order/reconnect cursor.
- Stable table locator qua parse/reorder/rename.
- Cascade table/column, reference factory và data-type impact sau khi tách.
- i18n key exhaustiveness cho validation code và agent event type.

### Component/integration test

- Trang mở với inspector đóng và Agent ở cột phải.
- Move Agent xuống dưới inspector, move lại bên phải, đóng và mở lại.
- Resize ngang/dọc bằng keyboard; mobile fallback hoạt động.
- Thay DBML/inspector → gọi validation draft → tô đúng table đỏ/vàng → tooltip có chi tiết.
- Request validation cũ trả muộn không thay kết quả mới.
- API validation lỗi hiển thị retry nhưng không đánh dấu table là validation error giả.
- Tạo/chuyển session; load history; load older events; clarification answer.
- Agent running/tool/proposal/error/completed render đúng; stream reconnect không duplicate.
- Accept/Reject proposal đồng bộ snapshot, diff, validation và timeline.
- Empty/error/loading states cho model, validation, session list và history.

### Regression và quality gate

- `npm run lint`
- `npm test`
- `npm run build`
- Kiểm tra không sửa tay `src/api/generated/`.
- Kiểm tra không import chéo feature.
- Script/checklist line limit cho source thủ công.
- Test trên Chrome/Edge với viewport desktop, laptop hẹp và mobile.

## 7. Thứ tự PR đề xuất

1. Backend draft-validation contract + OpenAPI generation.
2. FE characterization, i18n/naming/dead-code cleanup.
3. Workspace resizable/dockable shell, chưa đổi business flow.
4. Validation sub-feature và ERD table markers.
5. Backend Agent session/event API + OpenAPI generation.
6. Agent multi-session/event UI và proposal integration.
7. Document/inspector/canvas SRP-DRY refactor.
8. Accessibility, responsive hardening và full regression.

Mỗi PR phải giữ build/test pass; không move toàn bộ 101 file và đổi behavior trong cùng một PR.

## 8. Tiêu chí nghiệm thu cuối

- Không còn `ai-insights` demo hoặc text/visual khiến Validation Engine bị hiểu là LLM insight.
- Mọi thay đổi draft mới nhất được Validation Engine deterministic phân tích mà không Save/LLM.
- Warning/error hiển thị đúng table trên ERD với màu, icon, count và tooltip accessible.
- Layout mặc định là DBML → ERD → Agent; “Chi tiết bảng” đóng khi vào trang.
- Agent chuyển được giữa right dock, dưới inspector và hidden; panel resize được bằng component shadcn.
- Có nhiều Agent session, history sau reload, clarification và timeline event quan sát được.
- Proposal vẫn bắt buộc Accept/Reject trước khi áp vào Data Model.
- Không tự định nghĩa Backend DTO; tất cả API dùng generated SDK/types.
- Không còn file thủ công >120 dòng logic hoặc function >25 dòng logic; không có function >3 tham số.
- Không còn resize primitive/UI primitive phổ biến tự viết trùng common/shadcn.
- Không còn hardcoded user-facing text; VI/EN và namespace đều type-safe.
- Lint, test, build và accessibility checks đều pass.
