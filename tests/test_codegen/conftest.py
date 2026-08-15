"""Fixture DBML dùng chung cho bộ kiểm thử Codegen."""

import pytest

# DBML nghiệp vụ Gọi xe (Ride-hailing) — khớp với INITIAL_DBML của frontend
# (frontend/src/features/modeling-dashboard/hooks/useErdModeling.ts) để hai phía không lệch nhau.
RIDE_HAILING_DBML: str = """// Định nghĩa Fact & Dimension Tables
Table Fact_Rides {
  ride_key int [pk, increment]
  driver_key int [ref: > Dim_Driver.driver_key]
  customer_key int [ref: > Dim_Customer.customer_key]
  fare_amount decimal(10,2)
  discount_amount decimal(10,2)
  trip_status varchar(20)
  created_at timestamp
}

Table Dim_Driver {
  driver_key int [pk]
  driver_natural_id varchar(50)
  full_name varchar(100)
  vehicle_type varchar(30)
  rating decimal(3,2)
}

Table Dim_Customer {
  customer_key int [pk]
  phone_number varchar(20)
  member_tier varchar(20)
}"""


@pytest.fixture
def ride_hailing_dbml() -> str:
    """Nội dung DBML mẫu cho miền nghiệp vụ Gọi xe."""
    return RIDE_HAILING_DBML
