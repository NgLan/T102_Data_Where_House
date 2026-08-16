/**
 * Custom Hook quản lý thêm/sửa/xóa trực tiếp các dòng thuộc tính cột trong HITL Data Grid
 */

import { useState } from 'react';
import { ColumnAttribute } from '../types/hitl.types';

const SAMPLE_FACT_COLUMNS: ColumnAttribute[] = [
  { id: '1', name: 'ride_key', dataType: 'INT', keyType: 'PK', isNullable: false },
  { id: '2', name: 'driver_key', dataType: 'INT', keyType: 'FK', isNullable: false },
  { id: '3', name: 'customer_key', dataType: 'INT', keyType: 'FK', isNullable: false },
  { id: '4', name: 'fare_amount', dataType: 'DECIMAL(10,2)', keyType: 'NONE', isNullable: false },
  { id: '5', name: 'discount_amount', dataType: 'DECIMAL(10,2)', keyType: 'NONE', isNullable: true },
  { id: '6', name: 'trip_status', dataType: 'VARCHAR(20)', keyType: 'NONE', isNullable: true },
];

function getDefaultColumns(tableName: string | null): ColumnAttribute[] {
  if (tableName === 'Dim_Driver') {
    return [
      { id: 'd1', name: 'driver_key', dataType: 'INT', keyType: 'PK', isNullable: false },
      { id: 'd2', name: 'driver_natural_id', dataType: 'VARCHAR(50)', keyType: 'NONE', isNullable: false },
      { id: 'd3', name: 'full_name', dataType: 'VARCHAR(100)', keyType: 'NONE', isNullable: true },
      { id: 'd4', name: 'vehicle_type', dataType: 'VARCHAR(30)', keyType: 'NONE', isNullable: true },
    ];
  }
  if (tableName === 'Dim_Customer') {
    return [
      { id: 'c1', name: 'customer_key', dataType: 'INT', keyType: 'PK', isNullable: false },
      { id: 'c2', name: 'phone_number', dataType: 'VARCHAR(20)', keyType: 'NONE', isNullable: true },
      { id: 'c3', name: 'member_tier', dataType: 'VARCHAR(20)', keyType: 'NONE', isNullable: true },
    ];
  }
  return SAMPLE_FACT_COLUMNS;
}

export function useHitlEditor(tableName: string | null) {
  const [columns, setColumns] = useState<ColumnAttribute[]>(() => getDefaultColumns(tableName));

  // Thêm dòng cột mới
  const handleAddColumn = () => {
    const newCol: ColumnAttribute = {
      id: `new_${Date.now()}`,
      name: `col_${columns.length + 1}`,
      dataType: 'VARCHAR(50)',
      keyType: 'NONE',
      isNullable: true,
    };
    setColumns((prev) => [...prev, newCol]);
  };

  // Cập nhật giá trị một trường của cột (thay any bằng value cụ thể)
  const handleUpdateColumn = (
    id: string,
    field: keyof ColumnAttribute,
    value: ColumnAttribute[keyof ColumnAttribute]
  ) => {
    setColumns((prev) =>
      prev.map((col) => (col.id === id ? { ...col, [field]: value } : col))
    );
  };

  // Xóa cột
  const handleDeleteColumn = (id: string) => {
    setColumns((prev) => prev.filter((col) => col.id !== id));
  };

  return {
    columns,
    setColumns,
    handleAddColumn,
    handleUpdateColumn,
    handleDeleteColumn,
  };
}
