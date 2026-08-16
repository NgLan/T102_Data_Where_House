/**
 * Presentation Component: Attribute Data Grid cột trái trong HITL Modal
 */

import React from 'react';
import { ColumnAttribute } from '../types/hitl.types';
import { ColumnRowItem } from './ColumnRowItem';
import { Button } from '@/common/components/ui/button';
import { Plus, TableProperties } from 'lucide-react';

export interface AttributeDataGridProps {
  columns: ColumnAttribute[];
  onAddColumn: () => void;
  onUpdateColumn: (id: string, field: keyof ColumnAttribute, value: ColumnAttribute[keyof ColumnAttribute]) => void;
  onDeleteColumn: (id: string) => void;
}

export const AttributeDataGrid: React.FC<AttributeDataGridProps> = ({
  columns,
  onAddColumn,
  onUpdateColumn,
  onDeleteColumn,
}) => {
  return (
    <div className="flex-1 flex flex-col p-3.5 overflow-hidden bg-white">
      <div className="flex justify-between items-center mb-3">
        <label className="flex items-center gap-1.5 text-xs font-bold text-slate-800 m-0">
          <TableProperties className="w-4 h-4 text-blue-600" />
          Chỉnh sửa Cột & Thuộc tính (Direct Edit):
        </label>
        <Button variant="secondary" size="sm" onClick={onAddColumn} className="text-xs py-1">
          <Plus className="w-3.5 h-3.5 mr-1 text-blue-600" /> Thêm Cột Mới
        </Button>
      </div>

      <div className="flex-1 border border-slate-200/80 rounded-xl overflow-y-auto bg-white dark-scrollbar">
        <table className="w-full text-left text-xs border-collapse">
          <thead className="bg-slate-50/90 text-slate-700 font-bold sticky top-0 border-b border-slate-200 z-10">
            <tr>
              <th className="p-2.5 border-r border-slate-200/80 font-semibold">Tên Cột (Attribute)</th>
              <th className="p-2.5 border-r border-slate-200/80 font-semibold">Kiểu Dữ Liệu</th>
              <th className="p-2.5 border-r border-slate-200/80 text-center w-24 font-semibold">Khóa (PK/FK)</th>
              <th className="p-2.5 border-r border-slate-200/80 text-center w-16 font-semibold">Nullable</th>
              <th className="p-2.5 text-center w-16 font-semibold">Thao tác</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {columns.map((col) => (
              <ColumnRowItem
                key={col.id}
                column={col}
                onUpdate={onUpdateColumn}
                onDelete={onDeleteColumn}
              />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

