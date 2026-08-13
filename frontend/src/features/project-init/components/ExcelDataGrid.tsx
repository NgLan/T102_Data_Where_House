/**
 * Presentation Component: Grid xem trước dữ liệu Excel (Read-Only)
 * Responsive table với sticky headers, status badges & column type tags
 */

import React from 'react';
import { ExcelPreviewRowDto } from '@/api/model/project.dto';
import { Table, Lock, Eye } from 'lucide-react';

export interface ExcelDataGridProps {
  fileName: string;
  rows: ExcelPreviewRowDto[];
}

const MOCK_ROWS: ExcelPreviewRowDto[] = [
  { stt: 1, ride_id: '1001', driver_id: '501', customer_id: '8812', fare_amount: 150000, status: 'COMPLETED', created_at: '2026-08-01 08:30:00' },
  { stt: 2, ride_id: '1002', driver_id: '502', customer_id: '8815', fare_amount: 85000, status: 'COMPLETED', created_at: '2026-08-01 09:15:00' },
  { stt: 3, ride_id: '1003', driver_id: '501', customer_id: '8820', fare_amount: 45000, status: 'CANCELLED', created_at: '2026-08-01 10:00:00' },
  { stt: 4, ride_id: '1004', driver_id: '503', customer_id: '8812', fare_amount: 210000, status: 'COMPLETED', created_at: '2026-08-01 11:20:00' },
];

const COLUMNS: { key: keyof ExcelPreviewRowDto; label: string; type: string }[] = [
  { key: 'stt', label: '#', type: 'INT' },
  { key: 'ride_id', label: 'ride_id', type: 'BIGINT' },
  { key: 'driver_id', label: 'driver_id', type: 'INT' },
  { key: 'customer_id', label: 'customer_id', type: 'INT' },
  { key: 'fare_amount', label: 'fare_amount', type: 'DECIMAL' },
  { key: 'status', label: 'status', type: 'VARCHAR' },
  { key: 'created_at', label: 'created_at', type: 'DATETIME' },
];

export const ExcelDataGrid: React.FC<ExcelDataGridProps> = ({ fileName, rows }) => {
  const displayRows: ExcelPreviewRowDto[] = rows.length > 0 ? rows : MOCK_ROWS;
  const displayFileName = fileName || 'Sheet1_RawRides.xlsx';

  return (
    <div className="border border-slate-200/80 rounded-2xl bg-white mt-3.5 overflow-hidden shadow-xs">
      {/* Toolbar Header */}
      <div className="bg-slate-50/80 px-4 py-2.5 border-b border-slate-200/80 flex justify-between items-center text-xs font-semibold text-slate-700">
        <div className="flex items-center gap-2">
          <Table className="w-3.5 h-3.5 text-blue-600" />
          <span className="text-slate-500 font-normal">Sheet Nguồn:</span>
          <span className="font-bold text-slate-800">{displayFileName}</span>
          <span className="text-[11px] bg-slate-200/70 px-2 py-0.5 rounded-full text-slate-600 font-semibold">
            {displayRows.length} dòng × {COLUMNS.length} cột
          </span>
        </div>

        <div className="flex items-center gap-1.5 text-[11px] text-slate-500 bg-white border border-slate-200 px-2.5 py-1 rounded-full font-semibold">
          <Lock className="w-3 h-3 text-slate-400" /> Read-Only Preview
        </div>
      </div>

      {/* Grid Table */}
      <div className="overflow-x-auto" style={{ maxHeight: '260px' }}>
        <table className="w-full border-collapse text-xs">
          <thead>
            <tr className="bg-slate-100/90 text-slate-600 font-bold border-b border-slate-200">
              {COLUMNS.map((col) => (
                <th
                  key={col.key}
                  className="border-r border-slate-200/80 px-3.5 py-2.5 sticky top-0 bg-slate-100/90 text-left font-mono text-[11px]"
                >
                  <div className="flex items-center justify-between gap-1">
                    <span>{col.label}</span>
                    <span className="text-[9px] font-bold text-slate-400 bg-white/80 px-1.5 py-0.5 rounded border border-slate-200/60">
                      {col.type}
                    </span>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {displayRows.map((row, i) => (
              <tr key={i} className="hover:bg-blue-50/30 transition-colors font-mono">
                <td className="border-r border-slate-100 px-3.5 py-2 bg-slate-50/50 font-bold text-slate-500 text-center">
                  {row.stt}
                </td>
                <td className="border-r border-slate-100 px-3.5 py-2 font-semibold text-slate-800">{row.ride_id}</td>
                <td className="border-r border-slate-100 px-3.5 py-2 text-slate-600">{row.driver_id}</td>
                <td className="border-r border-slate-100 px-3.5 py-2 text-slate-600">{row.customer_id}</td>
                <td className="border-r border-slate-100 px-3.5 py-2 text-emerald-700 font-bold">
                  {row.fare_amount.toLocaleString('vi-VN')} đ
                </td>
                <td className="border-r border-slate-100 px-3.5 py-2">
                  <span
                    className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-bold ${
                      row.status === 'COMPLETED'
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        : 'bg-rose-50 text-rose-700 border border-rose-200'
                    }`}
                  >
                    {row.status}
                  </span>
                </td>
                <td className="px-3.5 py-2 text-slate-400 text-[11px]">{row.created_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

