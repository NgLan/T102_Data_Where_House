# Kế hoạch refactor UC5.1.3 – ERD Canvas và chỉnh sửa bảng

## Tóm tắt

Thay canvas tự vẽ bằng `@xyflow/react` và `elkjs`, tổ chức Step 2 theo bố cục DBML editor – ERD canvas – inspector giống nhóm công cụ dbdiagram. Một `DbmlDocument` draft là nguồn dữ liệu duy nhất cho code, bảng, cột và relationship.

## Thay đổi chính

- Tạo `ModelingWorkspace` điều phối DBML, canvas, inspector, save và revision conflict.
- Chuyển table editor UC5.1.3 khỏi modal toàn màn hình sang inspector dock bên phải.
- Dùng React Flow cho node, edge, pan, zoom, fit view, minimap và thao tác nối field; dùng ELK cho auto-layout.
- Hỗ trợ thêm/sửa/xóa bảng, cột và relationship one-to-one, one-to-many, many-to-one, kể cả composite endpoints.
- Lưu position/viewport theo project trong localStorage; position không được ghi vào DBML hoặc backend.
- Tên React component dùng `PascalCase.tsx`; hook, service, type và utility dùng `kebab-case`.
- Không sửa backend, OpenAPI hoặc generated API. Ngoại lệ ngoài `features` chỉ gồm dependency, wiring `page.tsx` và locale VI/EN.

## Kiểm thử

- Test reducer, validation, graph mapping, layout persistence và DBML sync hai chiều.
- Test chọn node/edge, inspector, tạo/xóa relationship, confirmation và keyboard interaction.
- Chạy `npm test`, `npm run lint`, `npm run build` và `git diff --check`.

## Tiêu chí hoàn thành

- Không còn connector SVG, zoom CSS, `INITIAL_TABLES` hoặc modal UC5.1.3 hard-code.
- Canvas không chồng node sau auto-layout và vẫn dùng được với ít nhất 20 bảng.
- Inspector không phủ canvas trên desktop; màn hình hẹp dùng drawer.
- Mọi text mới dùng i18n và code tuân thủ `TECHNICAL_CODING_GUIDELINES.md`.
