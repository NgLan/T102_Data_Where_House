# Kế hoạch refactor `frontend/src/common`

## Kết luận audit

`common` build, lint và test thành công nhưng chưa tuân thủ đầy đủ guideline về
FSD, SRP, DRY, naming, i18n và API nullable. Các vi phạm chính gồm mã chỉ phục vụ
một feature nhưng nằm trong `common`, mã chết/legacy, component và thuật toán tự
viết dù đã có thư viện/registry, contract API bị định nghĩa lặp và namespace i18n
quá rộng hoặc không được đăng ký.

## Thay đổi

- Xóa mã chết; chuyển DBML và text diff về `modeling-dashboard`; chuyển mapper lỗi
  form về `project-management`; tách utility sandbox theo một trách nhiệm.
- Dùng `diff` và `sql-formatter`; dùng component Toast/Tooltip của shadcn; bỏ các
  store Zustand và nhánh Axios không còn consumer.
- Tách helper API nullable và required; giữ endpoint `204` trả `void`; dùng type
  lỗi generated và sinh Zod schema từ OpenAPI.
- Chuẩn hóa filename/component, TSDoc và namespace/key i18n; xóa resource legacy,
  chia nhỏ resource modeling theo sub-feature.
- Bảo toàn logic HMR trong `i18n.ts`, giá trị `Data Warehouse Studio` và mọi thay
  đổi ngoài phạm vi đang có trong worktree.

## Kiểm thử chấp nhận

- Test payload bắt buộc, nullable và `204`; error classification/notification;
  confirmation dialog, DBML round-trip, text diff, SQL formatter và i18n parity.
- Chạy `npm run api:generate`, `npm run lint`, `npm test`, `npm run build`.
- Không sửa thủ công code generated và không còn import đến file đã xóa.
