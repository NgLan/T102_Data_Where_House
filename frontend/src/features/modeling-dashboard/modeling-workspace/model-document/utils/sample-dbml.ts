/** Mô hình rỗng dùng làm state khởi tạo của workspace.
 *
 * Cố ý KHÔNG chứa bảng mẫu nào: workspace phải mở với đúng mô hình của dự án. Trước đây
 * state khởi tạo là `SAMPLE_DBML` bên dưới và bộ bảng demo đó bị hiển thị nguyên vẹn mỗi
 * khi dự án chưa có Data Model, khiến người dùng tưởng dữ liệu bị fix cứng.
 */
export const EMPTY_DBML = "";

/** Mô hình mẫu dùng làm fixture cho unit test — KHÔNG dùng trong luồng chạy thật. */
export const SAMPLE_DBML = `Table rides {
  ride_id int [pk, increment]
  driver_id int [not null]
  customer_id int [not null]
  fare decimal(10,2)
  created_at timestamp
}

Table drivers {
  driver_id int [pk]
  full_name varchar(100)
  rating decimal(3,2)
}

Table customers {
  customer_id int [pk]
  phone_number varchar(20)
  member_tier varchar(20)
}

Ref: rides.driver_id > drivers.driver_id
Ref: rides.customer_id > customers.customer_id`;
