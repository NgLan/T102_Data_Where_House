# Kế hoạch refactor Project Management và App Shell

## Kết luận audit

`project-management` đã dùng generated API types/Zod, i18n, skeleton, empty/error
state, confirmation khi xóa và card đã hiển thị `description`. Tuy nhiên feature
chưa tuân thủ đầy đủ guideline về SRP, DRY, giới hạn function/file, FSD, naming và
tái sử dụng thư viện: form và server-state còn quản lý thủ công, các sub-feature
chưa được tách, domain options/field wrapper bị lặp và API danh sách chưa cung cấp
trạng thái DBML outdated.

## Thay đổi

- Tách `project-creation` và `project-list`; giữ screen/barrel ở root và chia nhỏ
  component/hook theo một trách nhiệm, tên mô tả, TSDoc đầy đủ.
- Dùng TanStack Query cho project cache/query/mutation dùng chung giữa header và
  danh sách; dùng React Hook Form + Zod/generated schema cho form tạo project.
- Cài component `field`, `avatar`, `dropdown-menu`, `badge` từ shadcn registry;
  tiếp tục tái sử dụng các primitive UI đã có.
- Thêm header vào `MainLayout`: logo, project switcher, VI/EN, light/dark và actor
  MVP. Logout hiển thị disabled cho đến khi có session authentication thật.
- Form tạo chỉ gửi tên, domain và mô tả tùy chọn; hỗ trợ danh sách domain mở rộng
  và input riêng khi chọn domain tùy chỉnh; không gửi raw requirement.
- Thêm `GET /api/v1/auth/me` và `is_data_model_outdated` trong project summary;
  đọc Data Model theo batch để không tạo N+1 query, sau đó sinh lại OpenAPI client.
- Chuẩn hóa field spacing, placeholder và semantic theme tokens trên toàn FE, giữ
  các editor/diff/terminal cố ý dùng giao diện tối.

## Contract và hành vi đã chốt

- `is_data_model_outdated` chỉ true khi DBML đã tồn tại và revision không còn
  khớp; project chưa có DBML không hiển thị cảnh báo.
- Mô tả dự án không bắt buộc và chuỗi rỗng được gửi thành `null`.
- Project switch điều hướng tới `/projects/{id}` và không giữ workflow step cũ.
- Runtime MVP luôn đăng nhập; chưa tạo login/register hoặc logout giả lập.
- Domain tĩnh gồm Ride-hailing, E-commerce, Bán lẻ, Ngân hàng–tài chính, Y tế,
  Giáo dục, Logistics, Sản xuất, Viễn thông, Du lịch–khách sạn và Tùy chỉnh.

## Kiểm thử chấp nhận

- Backend: current actor, batch model lookup và stale/current/missing DBML.
- Frontend: schema/custom domain/description, query cache và mutations, card/list
  states, header navigation/language/theme/user menu, field accessibility.
- Chạy `npm run api:generate`, `npm run lint`, `npm test`, `npm run build` cùng
  kiểm tra Python phù hợp; không sửa code generated bằng tay và không cần migration.
