# Kế hoạch refactor `frontend/src/api`

## Mục tiêu

Refactor `src/api` theo hướng tăng dần: code giao tiếp HTTP và transport type được sinh từ OpenAPI, còn `src/api/index.ts` là public entry point duy nhất được viết tay. Trong đợt hiện tại chỉ migrate Data Model vì đây là API nghiệp vụ duy nhất đã có generated SDK.

`openapi.json` thuộc quyền sở hữu của generator/backend, không được thêm endpoint hoặc chỉnh sửa schema bằng tay. Các file trong `src/api/generated` cũng không được chỉnh sửa trực tiếp.

## Đợt hiện tại

- Tạo `src/api/index.ts` để cấu hình generated client, thêm `X-Request-ID`, export `apiClient`, SDK functions và generated types.
- Các consumer của Data Model chỉ import qua `@/api`; giữ nguyên response unwrapping và `throwOnError`.
- Xóa `src/api/http/generated-client.ts` sau khi không còn consumer.
- Giữ nguyên Axios client, endpoint constants, DTO thủ công và các feature service chưa có endpoint tương ứng trong OpenAPI.
- Không tích hợp thêm `healthCheck` vì frontend chưa sử dụng endpoint này.

## Giai đoạn sau

Khi backend bổ sung contract và `openapi.json` được sinh lại bằng `npm run api:generate`, migrate lần lượt Project Init, Modeling, HITL và Sandbox sang `@/api`. Chỉ xóa `src/api/http`, `src/api/model` và dependency Axios sau khi không còn consumer.

## Tiêu chí hoàn thành

- `npm run lint` và `npm run build` thành công.
- Data Model tiếp tục gọi đúng `/api/v1/projects/{project_id}/data-model`, gửi `X-Request-ID` và giữ nguyên hành vi success/error.
- Phần Data Model không còn deep import từ `@/api/generated` hoặc tham chiếu tới `generated-client.ts`.
- `openapi.json` và toàn bộ `src/api/generated` không thay đổi trong đợt refactor này.
- Các feature chưa có generated endpoint vẫn hoạt động qua Axios như hiện tại.
