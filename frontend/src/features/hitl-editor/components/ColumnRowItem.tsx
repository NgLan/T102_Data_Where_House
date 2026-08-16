/**
 * Presentation Component: Dòng chi tiết thuộc tính 1 cột trong Attribute Data Grid
 */

import React from 'react';
import { ColumnAttribute } from '../types/hitl.types';
import { Input } from '@/common/components/ui/input';
import { Select } from '@/common/components/ui/select';
import { Trash2, Key, Link2 } from 'lucide-react';

export interface ColumnRowItemProps {
  column: ColumnAttribute;
  onUpdate: (id: string, field: keyof ColumnAttribute, value: ColumnAttribute[keyof ColumnAttribute]) => void;
  onDelete: (id: string) => void;
}

export const ColumnRowItem: React.FC<ColumnRowItemProps> = ({ column, onUpdate, onDelete }) => {
  return (
    <tr className="hover:bg-blue-50/20 transition-colors font-mono">
      <td className="p-1.5 border-r border-slate-100">
        <Input
          value={column.name}
          onChange={(e) => onUpdate(column.id, 'name', e.target.value)}
          className="py-1 text-xs font-mono bg-slate-50/50 focus:bg-white border-slate-200"
        />
      </td>

      <td className="p-1.5 border-r border-slate-100">
        <Select
          value={column.dataType}
          onChange={(e) => onUpdate(column.id, 'dataType', e.target.value)}
          className="py-1 text-xs font-mono bg-slate-50/50 focus:bg-white border-slate-200"
        >
          <option value="INT">INT</option>
          <option value="BIGINT">BIGINT</option>
          <option value="VARCHAR(20)">VARCHAR(20)</option>
          <option value="VARCHAR(50)">VARCHAR(50)</option>
          <option value="VARCHAR(100)">VARCHAR(100)</option>
          <option value="DECIMAL(10,2)">DECIMAL(10,2)</option>
          <option value="TIMESTAMP">TIMESTAMP</option>
          <option value="BOOLEAN">BOOLEAN</option>
        </Select>
      </td>

      <td className="p-1.5 border-r border-slate-100 text-center">
        <Select
          value={column.keyType}
          onChange={(e) => onUpdate(column.id, 'keyType', e.target.value as ColumnAttribute['keyType'])}
          className={`py-1 text-xs font-bold ${
            column.keyType === 'PK'
              ? 'text-blue-600 bg-blue-50 border-blue-200'
              : column.keyType === 'FK'
              ? 'text-emerald-600 bg-emerald-50 border-emerald-200'
              : 'text-slate-600 bg-slate-50/50'
          }`}
        >
          <option value="NONE">None</option>
          <option value="PK">PK 🔑</option>
          <option value="FK">FK 🔗</option>
        </Select>
      </td>

      <td className="p-1.5 border-r border-slate-100 text-center">
        <input
          type="checkbox"
          checked={column.isNullable}
          onChange={(e) => onUpdate(column.id, 'isNullable', e.target.checked)}
          className="w-4 h-4 text-blue-600 rounded border-slate-300 cursor-pointer accent-blue-600"
        />
      </td>

      <td className="p-1.5 text-center">
        <button
          onClick={() => onDelete(column.id)}
          className="text-slate-400 hover:text-rose-600 hover:bg-rose-50 p-1.5 rounded-lg transition-colors cursor-pointer"
          title="Xóa cột này"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      </td>
    </tr>
  );
};

