export const DEFAULT_DDL = `CREATE SCHEMA IF NOT EXISTS sandbox_dwh;

CREATE TABLE sandbox_dwh.Dim_Driver (
    driver_key INT PRIMARY KEY,
    driver_natural_id VARCHAR(50) NOT NULL,
    full_name VARCHAR(100),
    vehicle_type VARCHAR(30),
    rating DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sandbox_dwh.Dim_Customer (
    customer_key INT PRIMARY KEY,
    phone_number VARCHAR(20),
    member_tier VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sandbox_dwh.Fact_Rides (
    ride_key INT PRIMARY KEY,
    driver_key INT REFERENCES sandbox_dwh.Dim_Driver(driver_key),
    customer_key INT REFERENCES sandbox_dwh.Dim_Customer(customer_key),
    fare_amount DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    trip_status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);`;
