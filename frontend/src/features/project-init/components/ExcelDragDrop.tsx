/**
 * Presentation Component: Khu vực kéo thả file Excel Nguồn
 * Glassmorphic Drag & Drop Zone với hiệu ứng hover glow & nút load sample
 */

import React from 'react';
import { FileSpreadsheet, UploadCloud, Zap, CheckCircle2 } from 'lucide-react';

export interface ExcelDragDropProps {
  onLoadSample: () => void;
}

export const ExcelDragDrop: React.FC<ExcelDragDropProps> = ({ onLoadSample }) => {
  return (
    <div className="mb-4 space-y-2">
      {/* Label Row */}
      <div className="flex justify-between items-center">
        <label className="flex items-center gap-1.5 text-xs font-bold text-slate-700 m-0">
          <FileSpreadsheet className="w-4 h-4 text-emerald-600" />
          Đẩy file Nguồn Excel (.xlsx, .xls)
        </label>

        <button
          onClick={onLoadSample}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-emerald-50 to-teal-50 text-emerald-700 border border-emerald-200/80 text-xs font-bold hover:from-emerald-100 hover:to-teal-100 transition cursor-pointer shadow-2xs hover:shadow-xs"
        >
          <Zap className="w-3.5 h-3.5 fill-emerald-500 text-emerald-500" />
          Nạp Dữ liệu Mẫu (Rides.xlsx)
        </button>
      </div>

      {/* Drag Zone */}
      <div
        className="group relative border-2 border-dashed border-slate-200 hover:border-emerald-500/80 rounded-2xl p-6 text-center bg-slate-50/60 hover:bg-emerald-50/30 cursor-pointer transition-all duration-300 shadow-2xs hover:shadow-md"
        onClick={onLoadSample}
      >
        <div className="w-12 h-12 mx-auto mb-2 rounded-2xl bg-emerald-100/80 text-emerald-600 flex items-center justify-center group-hover:scale-110 group-hover:bg-emerald-500 group-hover:text-white transition-all duration-300 shadow-xs">
          <UploadCloud className="w-6 h-6" />
        </div>

        <b className="block text-slate-800 text-xs font-bold mb-1">
          Kéo thả file Excel (.xlsx / .xls) vào đây hoặc bấm để chọn file
        </b>

        <p className="text-[11px] text-slate-400 max-w-lg mx-auto m-0 leading-relaxed">
          Tự động đọc tất cả các Sheets, nhận diện schema thô & hiển thị preview bên dưới (Read-Only)
        </p>

        {/* Supported Format Badges */}
        <div className="flex justify-center items-center gap-2 mt-3 text-[10px] text-slate-400 font-medium">
          <span className="px-2 py-0.5 rounded-full bg-white border border-slate-200 text-slate-500">.XLSX</span>
          <span className="px-2 py-0.5 rounded-full bg-white border border-slate-200 text-slate-500">.XLS</span>
          <span className="px-2 py-0.5 rounded-full bg-white border border-slate-200 text-slate-500">.CSV</span>
          <span className="flex items-center gap-1 text-emerald-600 font-semibold">
            <CheckCircle2 className="w-3 h-3" /> Auto Detect Sheets
          </span>
        </div>
      </div>
    </div>
  );
};

