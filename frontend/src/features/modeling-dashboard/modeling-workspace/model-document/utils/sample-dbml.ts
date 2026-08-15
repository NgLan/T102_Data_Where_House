/** DBML hợp lệ dùng cho workspace local khi chưa có project snapshot. */
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
