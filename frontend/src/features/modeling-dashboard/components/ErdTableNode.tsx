/**
 * Presentation Component: ERD Node đại diện 1 bảng trong visual canvas
 * Thẻ hiển thị bảng với Fact/Dimension header gradients, PK/FK badges & hover elevation
 */

import React from 'react';
import { ErdTableNodeDto, ErdFieldDto } from '@/api/model/erd.dto';
import { Key, Link2, Sparkles, Edit3 } from 'lucide-react';

export interface ErdTableNodeProps {
  table: ErdTableNodeDto;
  onDoubleClick: (tableName: string) => void;
}

export const ErdTableNode: React.FC<ErdTableNodeProps> = ({ table, onDoubleClick }) => {
  const isFact = table.table_type === 'fact';

  return (
    <div
      className="absolute bg-white/95 rounded-xl border border-slate-200/90 w-[225px] shadow-md hover:shadow-xl hover:border-blue-500/80 text-xs cursor-pointer transition-all duration-200 overflow-hidden hover:-translate-y-1 z-10 group"
      style={{
        top: table.position?.top ?? 30,
        left: table.position?.left ?? 40,
      }}
      onDoubleClick={() => onDoubleClick(table.table_name)}
    >
      {/* Table Header Gradient */}
      <div
        className={`px-3 py-2 font-bold text-white flex justify-between items-center ${
          isFact
            ? 'bg-gradient-to-r from-blue-600 to-indigo-600 shadow-xs'
            : 'bg-gradient-to-r from-emerald-600 to-teal-600 shadow-xs'
        }`}
      >
        <div className="flex items-center gap-1.5 truncate">
          <span className="truncate">{table.table_name}</span>
        </div>

        <div className="flex items-center gap-1">
          <span className="text-[9px] font-bold px-1.5 py-0.2 bg-white/20 backdrop-blur-xs rounded text-white uppercase">
            {isFact ? 'FACT' : 'DIM'}
          </span>
          <Edit3 className="w-3 h-3 text-white/70 group-hover:text-white transition" />
        </div>
      </div>

      {/* Field Items List */}
      <div className="py-1 divide-y divide-slate-100/60">
        {table.fields.map((field: ErdFieldDto) => (
          <div
            key={field.name}
            className={`px-3 py-1.5 flex justify-between items-center font-mono text-[11px] transition-colors ${
              field.is_pk
                ? 'bg-blue-50/60 text-blue-900 font-bold'
                : field.is_fk
                ? 'bg-emerald-50/50 text-emerald-900 font-semibold'
                : 'text-slate-700 hover:bg-slate-50'
            }`}
          >
            <div className="flex items-center gap-1.5 truncate">
              {field.is_pk && (
                <span className="text-[9px] bg-blue-600 text-white font-bold px-1 rounded flex items-center gap-0.5">
                  <Key className="w-2.5 h-2.5" /> PK
                </span>
              )}
              {field.is_fk && (
                <span className="text-[9px] bg-emerald-600 text-white font-bold px-1 rounded flex items-center gap-0.5">
                  <Link2 className="w-2.5 h-2.5" /> FK
                </span>
              )}
              <span className="truncate">{field.name}</span>
            </div>

            <span className="text-[10px] text-slate-400 font-mono ml-2 flex-shrink-0">
              {field.type}
            </span>
          </div>
        ))}
      </div>

      {/* Double-click Hint Footer */}
      <div className="bg-slate-50/80 px-2.5 py-1 text-[10px] text-slate-400 font-sans border-t border-slate-100 flex items-center justify-between">
        <span>Double-click to edit</span>
        <span className="text-blue-500 font-semibold group-hover:underline">HITL →</span>
      </div>
    </div>
  );
};

