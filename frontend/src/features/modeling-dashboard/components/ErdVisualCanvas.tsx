/**
 * Presentation Component: ERD Visual Canvas - Khu vực hiển thị sơ đồ ERD kéo thả
 * Blueprint dot-grid canvas với đường nối SVG quan hệ FK-PK & Zoom Controls
 */

import React from 'react';
import { ErdTableNodeDto } from '@/api/model/erd.dto';
import { ErdTableNode } from './ErdTableNode';
import { Map, ZoomIn, ZoomOut, MousePointerClick, Layers } from 'lucide-react';

export interface ErdVisualCanvasProps {
  tables: ErdTableNodeDto[];
  zoomLevel: number;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onTableDoubleClick: (tableName: string) => void;
}

export const ErdVisualCanvas: React.FC<ErdVisualCanvasProps> = ({
  tables,
  zoomLevel,
  onZoomIn,
  onZoomOut,
  onTableDoubleClick,
}) => {
  return (
    <div
      className="flex flex-col rounded-2xl border border-slate-200/90 overflow-hidden bg-slate-100/70 shadow-sm relative"
      style={{ flex: 6 }}
    >
      {/* Canvas Toolbar Header */}
      <div className="bg-white/90 backdrop-blur-xs px-4 py-2.5 border-b border-slate-200/80 flex justify-between items-center text-xs font-semibold text-slate-700">
        <div className="flex items-center gap-2">
          <Map className="w-4 h-4 text-indigo-600" />
          <span className="font-bold tracking-tight text-slate-800">ERD VISUAL CANVAS</span>
          <span className="text-[10px] bg-indigo-50 text-indigo-700 border border-indigo-200 px-2 py-0.5 rounded-full font-bold">
            {tables.length} Tables Connected
          </span>
        </div>

        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5 text-[11px] text-emerald-700 bg-emerald-50 border border-emerald-200/80 px-2.5 py-1 rounded-full font-semibold">
            <MousePointerClick className="w-3 h-3 text-emerald-600 animate-bounce" />
            Nhấn đúp (Double-click) vào bảng để sửa HITL
          </span>

          <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded-xl border border-slate-200">
            <button
              onClick={onZoomIn}
              className="p-1 rounded-lg text-slate-600 hover:bg-white hover:text-blue-600 hover:shadow-2xs transition cursor-pointer"
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
            <span className="text-[10px] font-mono px-1.5 text-slate-500 font-bold">
              {Math.round(zoomLevel * 100)}%
            </span>
            <button
              onClick={onZoomOut}
              className="p-1 rounded-lg text-slate-600 hover:bg-white hover:text-blue-600 hover:shadow-2xs transition cursor-pointer"
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Interactive Canvas Area */}
      <div
        className="flex-1 relative overflow-auto select-none"
        style={{
          backgroundImage: 'radial-gradient(#cbd5e1 1.2px, transparent 1.2px)',
          backgroundSize: '20px 20px',
          padding: '24px',
          transform: `scale(${zoomLevel})`,
          transformOrigin: 'top left',
          transition: 'transform 0.2s ease-out',
        }}
      >
        {/* SVG Relationship Connector Lines */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none z-0" style={{ minWidth: '800px', minHeight: '500px' }}>
          <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#3b82f6" />
            </marker>
          </defs>

          {/* Connection line: Fact_Rides -> Dim_Driver */}
          <path
            d="M 235 90 C 275 90, 275 90, 315 90"
            fill="none"
            stroke="#2563eb"
            strokeWidth="2"
            strokeDasharray="4 3"
          />
          <text x="260" y="80" fill="#2563eb" fontSize="10" fontWeight="bold" fontFamily="monospace">1 : N</text>

          {/* Connection line: Fact_Rides -> Dim_Customer */}
          <path
            d="M 235 150 C 275 150, 275 290, 315 290"
            fill="none"
            stroke="#10b981"
            strokeWidth="2"
            strokeDasharray="4 3"
          />
          <text x="260" y="220" fill="#10b981" fontSize="10" fontWeight="bold" fontFamily="monospace">1 : N</text>
        </svg>

        {/* ERD Table Nodes */}
        {tables.map((table) => (
          <ErdTableNode
            key={table.table_name}
            table={table}
            onDoubleClick={onTableDoubleClick}
          />
        ))}
      </div>
    </div>
  );
};

