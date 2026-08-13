/**
 * Custom Hook quản lý DBML DSL, ERD Canvas Zoom/Pan & double-click trigger HITL Modal
 */

import { useState } from 'react';
import { useProjectStore } from '@/common/stores/useProjectStore';
import { ErdTableNodeDto } from '@/api/model/erd.dto';

const INITIAL_DBML = `// Định nghĩa Fact & Dimension Tables
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
}`;

const INITIAL_TABLES: ErdTableNodeDto[] = [
  {
    table_name: 'Fact_Rides',
    table_type: 'fact',
    position: { top: 30, left: 40 },
    fields: [
      { name: 'ride_key', type: 'INT', is_pk: true },
      { name: 'driver_key', type: 'INT', is_fk: true, ref_table: 'Dim_Driver' },
      { name: 'customer_key', type: 'INT', is_fk: true, ref_table: 'Dim_Customer' },
      { name: 'fare_amount', type: 'DECIMAL' },
      { name: 'discount_amount', type: 'DECIMAL' },
      { name: 'trip_status', type: 'VARCHAR' },
    ],
  },
  {
    table_name: 'Dim_Driver',
    table_type: 'dimension',
    position: { top: 40, left: 340 },
    fields: [
      { name: 'driver_key', type: 'INT', is_pk: true },
      { name: 'driver_natural_id', type: 'VARCHAR' },
      { name: 'full_name', type: 'VARCHAR' },
      { name: 'vehicle_type', type: 'VARCHAR' },
    ],
  },
  {
    table_name: 'Dim_Customer',
    table_type: 'dimension',
    position: { top: 250, left: 340 },
    fields: [
      { name: 'customer_key', type: 'INT', is_pk: true },
      { name: 'phone_number', type: 'VARCHAR' },
      { name: 'member_tier', type: 'VARCHAR' },
    ],
  },
];

export function useErdModeling() {
  const openHitlModal = useProjectStore((state) => state.openHitlModal);

  const [dbmlCode, setDbmlCode] = useState<string>(INITIAL_DBML);
  const [tables] = useState<ErdTableNodeDto[]>(INITIAL_TABLES);
  const [zoomLevel, setZoomLevel] = useState<number>(100);

  // Xử lý zoom canvas
  const handleZoomIn = () => setZoomLevel((prev) => Math.min(prev + 10, 150));
  const handleZoomOut = () => setZoomLevel((prev) => Math.max(prev - 10, 70));

  // Bắt sự kiện double-click trên thẻ node bảng để kích hoạt mở HITL Modal
  const handleTableDoubleClick = (tableName: string) => {
    openHitlModal(tableName);
  };

  return {
    dbmlCode,
    setDbmlCode,
    tables,
    zoomLevel,
    handleZoomIn,
    handleZoomOut,
    handleTableDoubleClick,
  };
}
