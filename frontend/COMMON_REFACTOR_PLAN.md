# Kế hoạch refactor `frontend/src/common` và chuẩn hóa coding guidelines

## 1. Mục tiêu và phạm vi

Refactor `frontend/src/common` theo Feature-Sliced Design, thay UI primitive tự viết bằng component cài từ shadcn CLI, gom locale vào module i18n, chuẩn hóa translation key và bổ sung quy tắc naming/doc-comment cho cả Frontend lẫn Backend.

Không thay đổi nghiệp vụ, API contract, `openapi.json` hoặc generated API code. Được phép sửa các consumer ngoài `common` khi cần đổi import, shadcn API, DBML adapter hoặc translation key.

Không tự xây parser/serializer DBML ở Frontend hoặc Backend. Dùng thư viện đã được duy trì và chỉ viết adapter/mapper mỏng thuộc ứng dụng. --> Cái nào tự viết rồi thì xóa đi.

## 2. Chuẩn hóa shadcn và Tailwind

- Đồng bộ Tailwind 4: giữ `postcss.config.mjs`, xóa cấu hình PostCSS/Tailwind 3 trùng lặp và chuyển `globals.css` sang cú pháp Tailwind 4.
- Khởi tạo shadcn latest với Radix, style `new-york`, base color `neutral`, CSS variables, React Server Components và TypeScript.
- Tạo `components.json` với các alias:
  - `ui`: `@/common/components/ui`
  - `utils`: `@/common/lib/utils`
  - `components`, `hooks`, `lib` trỏ vào các thư mục tương ứng trong `common`.
- Cài bằng shadcn CLI các component đang thực sự dùng: `button`, `input`, `textarea`, `native-select`, `alert-dialog`.
- Migrate consumer sang API chuẩn: `primary` thành variant mặc định, `danger` thành `destructive`, select HTML thành `NativeSelect`, confirmation dialog thành compound API của `AlertDialog`.
- Xóa UI tự viết hoặc không còn consumer: `badge`, `card`, `table`, `select`, `dialog`; không cài component chỉ để dự phòng.
- Giữ giao diện hiện tại bằng semantic CSS variables và `className` tại consumer; không nhúng style nghiệp vụ vào registry component.

Tham chiếu: [shadcn Next.js installation](https://ui.shadcn.com/docs/installation/next) và [components.json](https://ui.shadcn.com/docs/components-json).

## 3. Thay parser DBML tự viết bằng thư viện

### Frontend

- Cài và khóa phiên bản ổn định của `@dbml/core`; dùng `Parser.parse(source, 'dbmlv2')` vì parser `dbml` cũ đã deprecated, và dùng `ModelExporter` cho chiều xuất DBML. API chính thức hỗ trợ parse DBML thành `Database` model và export model trở lại DBML: [DBML JavaScript module](https://dbml.dbdiagram.io/js-module/core/).
- Xóa toàn bộ regex/scanner/parser/serializer DBML tự viết hiện tại. Không thay bằng một bộ parser nội bộ được chia nhỏ.
- Chỉ giữ hai application adapter nhỏ:
  - `dbml-adapter.ts`: gọi thư viện, chuẩn hóa parse result/error và không chứa grammar/regex DBML.
  - `dbml-mapper.ts`: ánh xạ `Database` model của thư viện sang view model editor và ngược lại; model thư viện không được leak vào component/store.
- Giữ Zod cho validation thuộc UI như required field, duplicate name và phản hồi theo từng field; không dùng Zod để tái hiện grammar DBML.
- Giữ public contract hiện tại cho feature ở mức `parseDbml(source) -> DbmlParseResult` và `serializeDbml(document) -> string` nếu có thể; implementation bên trong phải delegate cho thư viện.
- Parser FE chỉ cung cấp phản hồi sớm. Backend vẫn là nguồn xác thực cuối cùng; lỗi backend phải được hiển thị qua `ErrorCode.INVALID_DBML_CONTENT`.
- Kiểm tra bundle production. Nếu `@dbml/core` không tương thích browser hoặc làm initial bundle tăng quá lớn, chuyển adapter sang dynamic import/Web Worker; không quay lại parser tự viết.

### Backend

- Pin `lark-dbml>=0.7,<0.8` và `pydbml>=1.2,<1.3` cùng dependency parser của chúng. `lark-dbml` xử lý DBML một dòng; PyDBML là fallback cho syntax note mà `lark-dbml` 0.7.0 nhận nhầm keyword. Không bổ sung scanner/regex để vá hai parser.
- Thay nội dung parser regex trong `domain/data_model/dbml.py` bằng validation facade mỏng gọi thư viện và chỉ đọc AST parser trả về.
- Facade chỉ được phép:
  - Kiểm tra input rỗng trước khi gọi thư viện.
  - Gọi parser thư viện.
  - Catch exception parse cụ thể của phiên bản đã pin, rồi translate sang `BusinessException(code=ErrorCode.INVALID_DBML_CONTENT, ...)` với exception chain được giữ bằng `raise ... from exc`.
- Xóa `ParsedDbmlTable`, regex grammar, scanner brace/quote và column parser. Giữ allowlist data type như một business invariant hiện có, kiểm tra trên AST thay vì tự parse source.
- Không để object hoặc exception của `lark-dbml`/PyDBML vượt qua Domain boundary. Entity và application service tiếp tục làm việc với snapshot DBML dạng `str` và exception chuẩn của dự án.
- Cập nhật guideline Clean Architecture: thư viện parser thuần, deterministic và không I/O được phép nằm sau domain facade khi nó hiện thực trực tiếp một invariant định dạng; framework, persistence và network library vẫn bị cấm trong Domain.

### Tính nhất quán FE/BE

- Tạo một corpus fixture DBML dùng chung gồm valid, invalid và edge cases: tables, schema-qualified names, composite keys, indexes, enums, notes, defaults, inline/standalone references, escaped quote và malformed input.
- Chạy cùng corpus qua `@dbml/core` và facade thư viện backend; chỉ dùng phần syntax được cả hai phía chấp nhận cho luồng editor hiện tại.
- Khi hai thư viện khác nhau về syntax, Backend quyết định kết quả cuối; ghi rõ khác biệt trong test fixture thay vì thêm regex vá parser.
- Nâng phiên bản parser phải đi qua dependency review, fixture compatibility test và kiểm tra license/security; không dùng floating `latest` trong lock/requirements.

## 4. Tổ chức lại `common`

- Chỉ đặt code trong `common` khi được ít nhất hai feature dùng, là application shell hoặc là cross-cutting concern.
- Giữ DBML view model, Zod UI schema và library adapter trong `common/dbml` vì Modeling và HITL cùng sử dụng.
- Chuyển DDL formatter, clipboard và download-file helper về `features/sandbox-deployment` vì hiện chỉ feature này sử dụng.
- Đổi tên hook/store sang kebab-case và cập nhật toàn bộ import:
  - `useAppNotification.ts` thành `use-app-notification.ts`.
  - `useProjectStore.ts` thành `use-project-store.ts`.
  - `useScreenStore.ts` thành `use-screen-store.ts`.
- Giữ `MainLayout.tsx` như application-shell component.
- Xóa dead code sau khi xác nhận không còn consumer: `AppHeader`, `LanguageSwitcher`, `useDebounce`, `useModalState` và `common/lib/Test-file`.
- Không hoàn tác các thay đổi chưa commit hiện có, bao gồm API refactor và các `Test-file` đã được đánh dấu xóa.

## 5. Chuẩn hóa i18n

- Di chuyển locale thành `common/i18n/locales/{vi,en}`; đổi filename feature sang kebab-case như `project-init.json`, `hitl-editor.json`.
- Namespace dùng kebab-case; cập nhật resource registration, type declaration, `useTranslation` và mọi consumer.
- Flatten translation key và dùng `UPPER_SNAKE_CASE`:
  - `BTN_*` cho action.
  - `TXT_*` cho title, label và nội dung tĩnh.
  - `MSG_*` cho trạng thái/thông báo.
  - `*_LABEL`, `*_PLACEHOLDER` cho form.
  - `errors.json` giữ chính xác Backend `ErrorCode`.
- Bảo đảm VI/EN có cùng key và cùng interpolation variables dạng `{{camelCaseParam}}`.
- Giữ file UTF-8, type-safe resources và không dùng `any` hoặc type cast để né kiểm tra key.

## 6. Bổ sung `TECHNICAL_CODING_GUIDELINES.md`

### Naming

- Frontend: folder và file kỹ thuật dùng `kebab-case`; React component dùng `PascalCase.tsx`; file shadcn giữ tên registry lowercase; test dùng `.test.ts(x)`.
- Frontend identifier: component/type/interface dùng `PascalCase`; function/variable dùng `camelCase`; constant dùng `UPPER_SNAKE_CASE`; boolean bắt đầu bằng `is/has/should/can`; handler nội bộ dùng `handle*`, callback prop dùng `on*`.
- Backend: package/module/function/variable dùng `snake_case`; class/exception/DTO dùng `PascalCase`; constant và enum value dùng `UPPER_SNAKE_CASE`; private member bắt đầu `_`.
- Backend interface giữ convention dự án `IName` và file `i_<name>.py`; test dùng `test_<behavior>.py`.

### Comment và docstring

- Viết tiếng Việt cho exported/public API và logic nội bộ không hiển nhiên; generated, migration và shadcn registry code được miễn.
- Frontend dùng TSDoc/JSDoc: mô tả mục đích, `@param` cho từng tham số, `@returns`, `@throws` cho lỗi chủ động hoặc được propagate, `@remarks` cho side effect, `@template` khi generic và `@example` khi cách dùng không rõ.
- Backend dùng Google-style docstring với `Args`, `Returns`, `Raises`, `Yields` khi phù hợp; public method phải nêu business/system exception có thể phát sinh.
- Không comment local variable hoặc dòng code hiển nhiên; comment phải giải thích contract, lý do hoặc ràng buộc thay vì diễn giải lại code.

### Tái sử dụng thư viện

- Trước khi tự viết parser, serializer, formatter, validator cú pháp, crypto hoặc protocol client, phải kiểm tra thư viện chuẩn/được duy trì sẵn có cho cả FE và BE.
- Ưu tiên thư viện có public API rõ ràng, type hints/types, license phù hợp, release còn được duy trì và test corpus tốt.
- Bọc thư viện bằng adapter/facade nhỏ để model và exception bên thứ ba không leak vào Domain, feature hoặc public application contract.
- Chỉ tự triển khai khi đã ghi ADR nêu rõ thiếu thư viện phù hợp, yêu cầu đặc thù và chi phí bảo trì; không fork grammar hoặc copy parser vào repo nếu chưa có phê duyệt.

Sửa các đoạn guideline cũ mâu thuẫn với convention mới, đặc biệt đường dẫn locale, Tailwind/shadcn, comment và quy định dependency thuần trong Domain.

## 7. Kiểm thử và tiêu chí hoàn thành

- Thêm Vitest/jsdom và Testing Library cùng script `npm test`.
- Unit test DBML adapter/mapper bằng corpus chung; xác nhận parse/export round-trip và mapping không làm mất table, column, constraint, reference, note hoặc metadata được hỗ trợ.
- Backend test facade với cùng corpus; xác nhận lỗi thư viện được translate thành `INVALID_DBML_CONTENT` và không leak exception bên thứ ba.
- Test i18n tự động kiểm tra parity VI/EN, regex key naming, error-code exception và interpolation parity.
- Component test Button variants, NativeSelect change và AlertDialog open/cancel/confirm bằng keyboard.
- Test Zustand state transition và các common hook còn giữ lại.
- Chạy `npm test`, `npm run lint`, `npm run build`, Ruff và Pytest.
- Kiểm tra production bundle để DBML parser không nằm trong initial chunk nếu chỉ editor cần dùng.
- Dùng `rg` xác nhận không còn custom DBML grammar/regex parser, import đường dẫn cũ, locale cũ, UI primitive tự viết hoặc translation key lowercase.

## 8. Giả định

- `@dbml/core` là parser/exporter chuẩn cho FE; `lark-dbml` kết hợp PyDBML là parser chuẩn sau facade BE.
- Backend là authority đối với tính hợp lệ của DBML; FE validation chỉ tối ưu trải nghiệm chỉnh sửa.
- Không refactor toàn bộ hardcoded text ngoài các consumer bị ảnh hưởng trong đợt này.
- Quy tắc docstring mới áp dụng ngay cho code trong phạm vi refactor; toàn bộ backend còn lại áp dụng dần theo boy-scout rule.
