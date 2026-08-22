# Kế hoạch refactor Sandbox Deployment

## 1. Phạm vi và kết luận audit

Tài liệu này là kế hoạch refactor, chưa bao gồm thay đổi implementation. Phạm vi audit chính là toàn bộ 16 file trong `frontend/src/features/sandbox-deployment/`. `TECHNICAL_CODING_GUIDELINES.md`, ba feature `project-init`, `project-management`, `modeling-dashboard`, generated API, i18n, dependencies và `frontend/src/common/components/ui/` được đọc để đối chiếu.

Kết luận: feature **chưa tuân thủ đầy đủ guideline**. Generated API và thư viện formatter đã được dùng đúng hướng, nhưng cấu trúc feature, SRP, giới hạn kích thước, form validation, i18n, xử lý API error, loading/error state và tái sử dụng common UI còn nhiều vi phạm.

Baseline ngày 2026-08-23:

- ESLint riêng `src/features/sandbox-deployment` pass.
- Hai test file hiện có pass 4/4 test.
- Pass lint/test không đồng nghĩa đạt guideline: `SandboxConfigCard.tsx` có 352 dòng và `use-sandbox-deploy.ts` có 289 dòng; nhiều component/handler vượt giới hạn 25 dòng logic.

### Điểm đang làm đúng

- Feature không import chéo từ feature khác.
- Service dùng generated operations/types từ `@/api`, `requireApiData` và `unwrapApiData`; không tự định nghĩa lại request/response Backend.
- `format-sql.ts` dùng `sql-formatter` đã được cài và duy trì, không tự viết SQL formatter.
- Các control đã có sẵn như `Button`, `Input`, `Field`, `Checkbox`, `ConfirmationDialog` được dùng tại một phần giao diện.
- Namespace `sandbox-deployment` đã được đăng ký cho VI/EN.
- File/folder kỹ thuật phần lớn dùng kebab-case; component dùng PascalCase.

## 2. Các vấn đề ưu tiên phải sửa

### P0 — Vi phạm guideline trực tiếp

1. **Sai vị trí public screen:** `components/SandboxDeploymentScreen.tsx` phải chuyển thành `sandbox-deployment/SandboxDeploymentScreen.tsx`; `index.ts` chỉ re-export screen ở root.
2. **Vi phạm SRP và giới hạn kích thước:**
   - `SandboxConfigCard.tsx` trộn header/status, form connection, validation ngầm, save/test actions, reset warning, deploy confirmation và terminal trong 352 dòng.
   - `use-sandbox-deploy.ts` trộn query DDL/config, form state, ba mutation, editor actions, download/clipboard, log mapping, notification và error handling trong 289 dòng.
3. **Form không dùng Zod/React Hook Form:** validation hiện chỉ kiểm tra host/database/port bằng `hasValidConfig`; không validate username, schema regex/length hoặc hiển thị lỗi dưới từng field. Generated `zSandboxConfigRequest` đã có constraints và phải là nguồn contract.
4. **Hardcode UI text:** hầu hết text trong `SandboxConfigCard.tsx`, `DdlActionsBar.tsx`, `DdlCodeEditor.tsx`, `ExecutionTerminal.tsx` và nhiều log/fallback trong `use-sandbox-deploy.ts` không đi qua i18n.
5. **Không tái sử dụng common UI:**
   - `DdlActionsBar.tsx` tự dùng `<button>` và `<select>` dù đã có `Button`, `NativeSelect`, `NativeSelectOption`.
   - `DdlCodeEditor.tsx` tự dùng `<textarea>` dù đã có `Textarea`.
   - Các status pill trong `SandboxConfigCard.tsx` tự dựng bằng `<span>` dù đã có `Badge`.
   - Initial load không có `Skeleton`; lỗi load bị đổi thành terminal log nên không có error state và nút retry rõ ràng.
6. **API error sai chuẩn:** các `catch` lấy `error.message`, hiển thị message kỹ thuật và phát toast generic; chưa dùng `handleApiError`/`isApiError` và `error_code` để dịch qua `errors.json`.

### P1 — Lỗi thiết kế, DRY và hành vi dễ sai

1. Đổi DDL dialect đang gọi lại cả config API vì `loadSandboxData` phụ thuộc `ddlDbType`; config không liên quan dialect và không nên bị refetch.
2. Query/mutation server state được quản lý thủ công bằng nhiều `useState`/`useEffect`; thiếu cache, invalidation, retry và chống response cũ ghi đè response mới. Nên theo mẫu các feature tham chiếu và dùng TanStack Query.
3. `ddlDbType` và `dbType` khó phân biệt. `dbType` của connection không có control chỉnh sửa nhưng vẫn được load/save ngầm; trong khi execution chỉ cho PostgreSQL. Cần chốt một contract rõ ràng:
   - Nếu sandbox chỉ hỗ trợ PostgreSQL, đổi tên thành `ddlDialect`, bỏ connection engine state và luôn gửi `EXECUTABLE_SANDBOX_DB_TYPE`.
   - Nếu sandbox hỗ trợ nhiều engine, phải có field `sandboxDbType` hiển thị/validate riêng và capability execution tương ứng.
4. Formatter luôn dùng PostgreSQL dù toolbar cho chọn PostgreSQL/Snowflake/BigQuery. `sql-formatter@15.8.2` đã hỗ trợ cả ba; cần map generated enum sang language của thư viện và test từng dialect.
5. `DDL_DB_TYPE_LABELS` là `Partial<Record<...>>`, sau đó `Object.keys(...) as SandboxDbType[]`; cách cast này che mất tính exhaustiveness. Cần khai báo danh sách dialect được hỗ trợ tường minh và dùng `satisfies`.
6. Kết nối đã báo thành công vẫn giữ trạng thái `success` sau khi người dùng sửa host/port/database/credentials. Bất kỳ thay đổi config nào phải reset connection result về `idle`.
7. `Number(value) || 5432` lập tức đổi field rỗng hoặc `0` thành `5432`, khiến người dùng không thể nhập/chỉnh lỗi tự nhiên. Form nên giữ input value, rồi Zod coerce/validate lúc submit/blur.
8. `isSchemaProtected` chỉ so sánh chính xác với `"public"`; chưa normalize khoảng trắng/case và có thể lệch rule Backend. FE chỉ dùng check này cho UX, Backend vẫn là nguồn bảo vệ cuối cùng; schema phải được normalize qua schema form.
9. Password đã lưu không được Backend trả về, nhưng UI gửi chuỗi rỗng khi test/save sau load. Cần characterization test và quy ước rõ `undefined`/`null`/chuỗi rỗng là “giữ password cũ” hay “xóa password”; không tự suy đoán trong UI.
10. Clipboard failure đang bị nuốt im lặng. Phải phát notification phù hợp; chuẩn hóa browser clipboard thành utility dùng chung vì `modeling-dashboard` cũng đang tự gọi `navigator.clipboard`.
11. Download utility không có test cleanup/error path. Native Blob/Object URL API là đủ, không cần thêm thư viện; giữ adapter nhỏ và test việc append/click/remove/revoke.
12. `ExecutionTerminal` dùng array index làm key, thiếu `role="log"`/`aria-live`, và hardcode empty state tiếng Anh. Log entry cần ID ổn định hoặc key tổng hợp ổn định.
13. Editor tự dựng gutter line-number nhưng không có syntax highlighting thật. Chọn một trong hai hướng, không tự viết editor nửa vời:
    - Nhu cầu chỉ là text editing: dùng common `Textarea`, bỏ gutter giả và giữ UI đơn giản như `DBMLEditor`.
    - Nhu cầu có line number/highlighting/keyboard editor thật: đánh giá và cài một editor được duy trì (ưu tiên CodeMirror 6 do modular và nhẹ hơn Monaco), bọc bằng adapter component; ghi ADR/dependency decision trước khi thêm package.

### P2 — Naming, dead code, coupling và test coverage

- `TerminalLogEntryDto` là view model chứ không phải Backend DTO; đổi thành `ExecutionLogEntry`. `StatementLogDto`, `SandboxConfigState`, `SandboxDeploymentState` không được dùng và phải xóa.
- `utils/default-ddl.ts` không được dùng; xóa thay vì giữ demo constant. Nếu sau này cần empty/default DDL, đặt trong `constants/` và chỉ thêm khi có consumer thật.
- Hậu tố `Api` trong `getSandboxConfigApi`, `saveSandboxConfigApi`... là dư vì file/service boundary đã thể hiện API; chuẩn hóa thành verb + noun như `getSandboxConfig`, `saveSandboxConfig`, `testSandboxConnection`, `executeSandboxDdl` ở adapter, đồng thời alias generated operation rõ ràng để tránh trùng tên.
- `DdlCodeEditorProps extends DdlActionsBarProps` làm editor phụ thuộc toàn bộ contract toolbar. Tách `DdlEditorProps` và `DdlEditorToolbarProps`, chỉ truyền object/callback đúng capability.
- `SandboxConfigCardProps` có quá nhiều field/callback và nhiều optional prop dù screen luôn truyền đủ. Thay bằng `UseFormReturn`/view model nhỏ hoặc chia props theo `form`, `connection`, `execution`.
- `React.FC` và default `React` import không cần thiết, không đồng nhất với feature mẫu. Dùng named function component và interface private trừ public API thật sự.
- Comment đầu file kiểu “Presentation Component”, “Line Numbers Column”, “Editor Footer” chỉ diễn giải code hiển nhiên và có tiếng Anh; xóa hoặc thay bằng TSDoc tiếng Việt mô tả contract/side effect.
- `sandbox-api.test.ts` chỉ test `getSandboxConfig`; chưa khóa request path/query/body, unwrap/require behavior của bốn operation còn lại.
- Chưa có test cho hooks, form validation, screen loading/error/retry, toolbar, confirmation reset, dialect guard, i18n và accessibility.

## 3. Audit theo từng file hiện tại

| File | Kết luận | Hành động |
|---|---|---|
| `index.ts` | Nội dung barrel đúng tối giản, nhưng export từ vị trí screen sai | Cập nhật export sang `./SandboxDeploymentScreen` |
| `components/SandboxDeploymentScreen.tsx` | Sai vị trí; fallback i18n hardcode; truyền hàng chục prop; chưa có skeleton/error/retry | Move ra root, chỉ orchestration các capability và render page states |
| `components/SandboxConfigCard.tsx` | 352 dòng, vi phạm SRP; form không Zod; text hardcode; status badge tự dựng; prop contract quá lớn | Thay bằng form, connection actions, status và execution panel riêng |
| `components/DdlActionsBar.tsx` | Tự dựng button/select; hardcode text; cast options không an toàn; contract export/coupling không cần thiết | Dùng common UI, i18n, danh sách dialect typed và tách toolbar props |
| `components/DdlCodeEditor.tsx` | Native textarea/gutter tự dựng; hardcode footer; thiếu accessible label; phụ thuộc toolbar props | Dùng `Textarea` hoặc thư viện editor đã chốt; tách toolbar/editor |
| `components/ExecutionTerminal.tsx` | Hardcode tiếng Anh, index key, thiếu live-region semantics | Đổi thành `ExecutionLog`, dịch toàn bộ text, dùng key ổn định và accessibility |
| `hooks/use-sandbox-deploy.ts` | 289 dòng, vi phạm SRP; manual server state; hardcode log/error; dual DB type mơ hồ | Xóa sau khi tách query/form/editor/execution hooks |
| `services/sandbox-api.ts` | Generated SDK đúng; file đang gom ba capability và naming dư `Api` | Tách service theo capability hoặc giữ một adapter dưới sub-feature nếu vẫn dưới 120 dòng; chuẩn hóa tên |
| `services/sandbox-api.test.ts` | Chỉ cover 1/5 adapter operations | Tách/đổi tên test theo source mới và cover toàn bộ request mapping |
| `constants/sandbox-db-options.ts` | Có source label tập trung nhưng không exhaustive và dựa vào cast | Tạo supported dialect options typed bằng `satisfies`; tách DDL dialect khỏi sandbox engine |
| `types/sandbox.types.ts` | Có ba type dead; suffix `Dto` sai nghĩa | Xóa dead type, đổi view model log và đặt cạnh execution capability |
| `utils/format-sql.ts` | Dùng thư viện đúng, nhưng cố định PostgreSQL | Đổi thành dialect-aware adapter, không tự viết formatter |
| `utils/format-sql.test.ts` | Test pass nhưng chỉ cover PostgreSQL/error | Test PostgreSQL, Snowflake, BigQuery, empty input và error propagation |
| `utils/copy-text-to-clipboard.ts` | Adapter nhỏ nhưng nuốt lỗi; logic clipboard lặp ở feature khác | Chuyển thành common browser utility có result/error contract và test |
| `utils/download-text-file.ts` | Native browser API phù hợp; format/comment chưa đồng nhất, thiếu test | Giữ colocated, chuẩn hóa code/TSDoc và thêm test cleanup |
| `utils/default-ddl.ts` | Dead/demo code | Xóa |

Ngoài phạm vi folder nhưng bắt buộc cập nhật cùng refactor: hai file `common/i18n/locales/{vi,en}/sandbox-deployment.json`; có nhiều key chưa được dùng, trong khi phần lớn text thực tế lại hardcode. `TXT_TARGET_DIALECT` cũng đang cố định PostgreSQL dù UI có nhiều dialect.

## 4. Cấu trúc thư mục đích

Giữ screen công khai ở root như ba feature tham chiếu và chia theo capability nghiệp vụ, không dồn toàn bộ code vào các folder kỹ thuật phẳng:

```text
sandbox-deployment/
├── SandboxDeploymentScreen.tsx
├── index.ts
├── constants/
│   ├── sandbox-deployment-query-keys.ts
│   └── supported-ddl-dialects.ts
└── sandbox-deployment-screen/
    ├── components/
    │   ├── SandboxDeploymentHeader.tsx
    │   ├── SandboxDeploymentSkeleton.tsx
    │   └── SandboxDeploymentLoadError.tsx
    ├── ddl-editor/
    │   ├── components/
    │   │   ├── DdlEditor.tsx
    │   │   └── DdlEditorToolbar.tsx
    │   ├── hooks/
    │   │   └── use-ddl-editor.ts
    │   ├── services/
    │   │   └── data-model-ddl-api.ts
    │   └── utils/
    │       ├── build-ddl-document.ts
    │       ├── download-text-file.ts
    │       └── format-ddl.ts
    ├── sandbox-config/
    │   ├── components/
    │   │   ├── SandboxConfigForm.tsx
    │   │   ├── SandboxConfigFields.tsx
    │   │   └── SandboxConnectionStatus.tsx
    │   ├── hooks/
    │   │   └── use-sandbox-config.ts
    │   ├── schemas/
    │   │   └── sandbox-config-form-schema.ts
    │   └── services/
    │       └── sandbox-config-api.ts
    └── sandbox-execution/
        ├── components/
        │   ├── DeploySandboxAction.tsx
        │   ├── ExecutionLog.tsx
        │   └── SandboxExecutionPanel.tsx
        ├── hooks/
        │   └── use-sandbox-execution.ts
        ├── services/
        │   └── sandbox-execution-api.ts
        ├── types/
        │   └── execution-log-types.ts
        └── utils/
            └── map-statement-log.ts
```

Không bắt buộc tạo mọi folder/file ngay lập tức. Chỉ tạo layer có consumer thật; nếu một file nhỏ không có trách nhiệm độc lập, giữ cùng capability thay vì tách máy móc.

## 5. Kế hoạch triển khai theo phase

### Phase 0 — Characterization và chốt contract

- [ ] Thêm test hành vi hiện tại cho load config + DDL, đổi dialect, save, test connection, execute success/partial failure/error và reset confirmation.
- [ ] Chốt semantics password rỗng/null/undefined với Backend và khóa bằng API/service test.
- [ ] Chốt sandbox engine chỉ PostgreSQL hay đa engine; không giữ hai state có tên mơ hồ.
- [ ] Chốt editor đơn giản bằng common `Textarea` hay editor library thật theo nhu cầu line number/highlighting.
- [ ] Ghi baseline test và đảm bảo không sửa generated source thủ công.

Điều kiện hoàn thành: các hành vi cần giữ đã có test, hai quyết định engine/editor được ghi rõ.

### Phase 1 — Sửa cấu trúc, dead code và naming

- [ ] Move `SandboxDeploymentScreen.tsx` ra root và cập nhật `index.ts`.
- [ ] Tạo `sandbox-deployment-screen/` và ba capability `ddl-editor`, `sandbox-config`, `sandbox-execution`.
- [ ] Đổi `DdlCodeEditor` thành `DdlEditor`, `DdlActionsBar` thành `DdlEditorToolbar`, `ExecutionTerminal` thành `ExecutionLog`.
- [ ] Đổi `TerminalLogEntryDto` thành `ExecutionLogEntry`; xóa ba type dead và `default-ddl.ts`.
- [ ] Chuẩn hóa API adapter theo verb + noun; chỉ export API public thật sự.
- [ ] Xóa comment hiển nhiên, chuẩn hóa TSDoc tiếng Việt và format quote/import theo repo.

Điều kiện hoàn thành: public screen/root đúng guideline; không còn dead code; mỗi file dưới 120 dòng logic.

### Phase 2 — Tách server state, form và commands

- [ ] Tạo query key ổn định theo project/dialect.
- [ ] Dùng `useQuery` riêng cho config và generated DDL; đổi dialect chỉ refetch DDL.
- [ ] Dùng `useMutation` riêng cho save config, test connection và execute DDL; invalidate/set query cache sau save.
- [ ] Tạo React Hook Form + `zodResolver`, reuse `zSandboxConfigRequest` để validate/normalize; hiển thị `FieldError` ngay dưới từng field.
- [ ] Reset connection status khi form thay đổi; giữ loading state initial và mutation state độc lập.
- [ ] Tách editor-local commands (format/copy/download) khỏi config/execution network state.
- [ ] Map API error qua hạ tầng error chung và `error_code`; không render trực tiếp `Error.message` kỹ thuật.
- [ ] Mọi callback/handler dài hơn 25 dòng phải tách thành mapper/command nhỏ có tên mô tả nghiệp vụ.

Điều kiện hoàn thành: không còn `use-sandbox-deploy.ts`; screen ghép các view model nhỏ và không biết chi tiết request payload.

### Phase 3 — Common UI, thư viện và accessibility

- [ ] Thay native buttons/select/textarea/status bằng `Button`, `NativeSelect`, `Textarea`, `Badge` hiện có.
- [ ] Dùng `Skeleton` cho initial load; tạo error state có mô tả và `Button` retry.
- [ ] Giữ `ConfirmationDialog`, `Checkbox`, `Field`, `Input` hiện có; không tạo component tương đương mới.
- [ ] Nếu cần editor thật, cài dependency đã chốt bằng package manager và lockfile, tạo adapter nhỏ; không tự viết syntax highlighter/gutter.
- [ ] Thêm `aria-label` cho editor, `role="log"`/`aria-live="polite"` cho log và focus behavior phù hợp sau mutation.
- [ ] Dùng key ổn định cho log; bảo đảm control có hover/focus/cursor theo common component.
- [ ] Chuyển clipboard adapter sang `common` và dùng lại ở sandbox cùng DBML editor để loại duplicate logic.

Điều kiện hoàn thành: không còn native UI primitive tự style khi common/shadcn đã có; keyboard/screen reader flow được test.

### Phase 4 — i18n và nội dung động

- [ ] Chuyển 100% title, label, button, status, warning, confirmation, empty state, aria text và local log sang translation key.
- [ ] Dùng `{{host}}`, `{{port}}`, `{{databaseName}}`, `{{dialect}}`, `{{duration}}`, `{{succeeded}}`, `{{executed}}` cho text động; không nối chuỗi hiển thị thủ công.
- [ ] Toast success/warning dùng `notifications.json`; Backend error dùng `errors.json`; text riêng feature dùng `sandbox-deployment.json`.
- [ ] Đồng bộ VI/EN, sửa `TXT_TARGET_DIALECT` thành key có parameter, xóa key stale/duplicate như `MSG_COPY_SUCCESS` nếu notification namespace đã sở hữu nội dung.
- [ ] Không dùng `t(key, hardcodedFallback)` để che key thiếu; thêm key đầy đủ và dựa vào typed namespace.

Điều kiện hoàn thành: scan không còn user-facing string hardcode và VI/EN có cùng bộ key.

### Phase 5 — Test và kiểm tra chấp nhận

- [ ] Service tests: đủ năm operation, path/query/body, `responseStyle`, `throwOnError`, nullable config và invalid envelope.
- [ ] Schema/form tests: host/database/schema required, length, schema regex, port 1–65535, trim/normalize và password semantics.
- [ ] Query/hook tests: config không refetch khi đổi dialect, stale request không ghi đè, cache cập nhật sau save, error code được giữ nguyên.
- [ ] Editor tests: format đúng từng dialect, copy success/failure, download SQL/Markdown và filename/MIME.
- [ ] Component tests: skeleton, load error + retry, field error, connection status reset, unsupported dialect guard, protected schema, destructive confirmation và execution summary.
- [ ] Accessibility tests: accessible names, keyboard action, live log region và disabled state.
- [ ] Chạy `npm run lint`, `npm test`, `npm run build`; nếu có thay đổi Backend/OpenAPI thì chạy `npm run api:generate` trước và xác nhận generated diff chỉ đến từ generator.

## 6. Tiêu chí hoàn tất

- Public screen ở root và `index.ts` chỉ export public API.
- Không file code thủ công nào vượt 120 dòng logic; không function/handler nào vượt 25 dòng logic hoặc 3 tham số.
- Config form dùng React Hook Form + Zod/generated schema và có lỗi theo field.
- Query/mutation dùng TanStack Query; không còn effect thủ công ghép config với DDL.
- Không còn UI text hardcode, fallback string hay API error message kỹ thuật hiển thị trực tiếp.
- Không còn button/select/textarea/badge/skeleton tự dựng khi common UI đã cung cấp.
- Formatter dùng `sql-formatter` đúng dialect; không có parser/formatter/editor feature tự viết nếu thư viện đã được chốt.
- Không còn dead type/default demo DDL; naming phản ánh đúng domain và callback/boolean đúng convention.
- Có đủ loading, error/retry, validation, confirmation và accessibility state.
- Toàn bộ test mới và cũ, lint và production build đều pass.

## 7. Ngoài phạm vi của lần refactor

- Không sửa tay generated API trong `frontend/src/api/generated/`.
- Không thay đổi Backend contract nếu chưa phát hiện contract hiện tại không thể biểu diễn password/engine semantics; nếu cần, tách thành task Backend + regenerate OpenAPI rõ ràng.
- Không thêm code editor library chỉ để làm đẹp. Chỉ thêm khi UX thật sự cần line number/highlighting/keyboard support và đã ghi dependency decision.
- Không refactor rộng `modeling-dashboard`; thay đổi ngoài sandbox chỉ giới hạn ở việc dùng chung clipboard utility nếu cần loại bỏ duplicate.
