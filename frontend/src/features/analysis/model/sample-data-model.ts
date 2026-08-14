export const CURRENT_MODEL_DBML = `// Ride Analytics Warehouse · revision 12
Table Fact_Rides {
  ride_key bigint [pk, increment, not null]
  driver_key int [ref: > Dim_Driver.driver_key, not null]
  customer_key int [ref: > Dim_Customer.customer_key, not null]
  promo_key int [ref: > Dim_Promo.promo_key]
  fare_amount decimal(12,2) [not null]
  discount_amount decimal(12,2)
  trip_status varchar(20) [not null]
  created_at timestamp [not null]
}

Table Dim_Driver {
  driver_key int [pk, increment, not null]
  driver_id varchar(50) [not null]
  full_name varchar(100) [not null]
  vehicle_type varchar(30)
  rating decimal(3,2)
}

Table Dim_Customer {
  customer_key int [pk, increment, not null]
  customer_id varchar(50) [not null]
  phone_number varchar(20)
  member_tier varchar(20)
}

Table Dim_Promo {
  promo_key int [pk, increment, not null]
  promo_code varchar(40) [not null]
  discount_type varchar(20) [not null]
  valid_from timestamp
  valid_to timestamp
}`;

export const CURRENT_MODEL = {
  model_name: "Ride Analytics Warehouse",
  revision: 12,
  dbml: CURRENT_MODEL_DBML,
} as const;
