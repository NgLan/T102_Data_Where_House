/**
 * Presentation Component: Form khởi tạo dự án (Domain, Dialect, Mô tả)
 * Glass card thiết kế sang trọng với gợi ý prompt thông minh
 */

import React from 'react';
import { Building2, Database, FileText, Sparkles, Car, ShoppingCart, Landmark, Cpu } from 'lucide-react';

export interface ProjectInitCardProps {
  domain: string;
  onDomainChange: (val: string) => void;
  dialect: string;
  onDialectChange: (val: string) => void;
  description: string;
  onDescriptionChange: (val: string) => void;
}

const PROMPT_SUGGESTIONS = [
  '🚗 Quản lý lịch trình chuyến đi & thông tin tài xế',
  '💰 Tính tổng doanh thu theo khu vực & khuyến mãi',
  '📊 Phân tích tỷ lệ hủy chuyến theo khung giờ peak',
];

export const ProjectInitCard: React.FC<ProjectInitCardProps> = ({
  domain,
  onDomainChange,
  dialect,
  onDialectChange,
  description,
  onDescriptionChange,
}) => {
  return (
    <div className="w-full space-y-4">
      {/* Card Header Title */}
      <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
        <div className="w-7 h-7 rounded-lg bg-blue-100/80 text-blue-600 flex items-center justify-center font-bold text-xs">
          1
        </div>
        <div>
          <h3 className="text-sm font-bold text-slate-800 m-0">Cấu hình Dự án & Ngữ cảnh Nghiệp vụ</h3>
          <p className="text-xs text-slate-400 m-0">Chọn lĩnh vực nghiệp vụ mẫu và hệ quản trị CSDL mục tiêu</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Domain Selection */}
        <div>
          <label className="flex items-center gap-1.5 text-xs font-bold text-slate-700 mb-1.5">
            <Building2 className="w-3.5 h-3.5 text-blue-600" />
            Lĩnh vực / Domain Nghiệp vụ
          </label>
          <div className="relative">
            <select
              className="w-full px-3.5 py-2.5 border border-slate-200 rounded-xl text-xs bg-slate-50/50 text-slate-800 font-semibold outline-none focus:border-blue-500 focus:bg-white focus:ring-3 focus:ring-blue-500/10 transition appearance-none cursor-pointer"
              value={domain}
              onChange={(e) => onDomainChange(e.target.value)}
            >
              <option value="ride">🚗 Dịch vụ Gọi xe (Ride-hailing / Grab / Gojek)</option>
              <option value="ecommerce">🛒 Thương mại Điện tử (E-commerce / Retail)</option>
              <option value="banking">🏦 Ngân hàng & Tài chính (Banking / Fintech)</option>
              <option value="custom">⚡ Tùy chỉnh nghiệp vụ riêng (Custom Schema)</option>
            </select>
            <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400 text-xs">
              ▼
            </div>
          </div>
        </div>

        {/* Target Dialect Selection */}
        <div>
          <label className="flex items-center gap-1.5 text-xs font-bold text-slate-700 mb-1.5">
            <Database className="w-3.5 h-3.5 text-indigo-600" />
            Target Dialect (Hệ quản trị CSDL DWH)
          </label>
          <div className="relative">
            <select
              className="w-full px-3.5 py-2.5 border border-slate-200 rounded-xl text-xs bg-slate-50/50 text-slate-800 font-semibold outline-none focus:border-blue-500 focus:bg-white focus:ring-3 focus:ring-blue-500/10 transition appearance-none cursor-pointer"
              value={dialect}
              onChange={(e) => onDialectChange(e.target.value)}
            >
              <option>🐘 PostgreSQL (Standard DW & Lakehouse)</option>
              <option>❄️ Snowflake Data Cloud</option>
              <option>🔍 Google BigQuery</option>
              <option>⚡ ClickHouse OLAP Engine</option>
            </select>
            <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400 text-xs">
              ▼
            </div>
          </div>
        </div>
      </div>

      {/* Business Requirement Description */}
      <div>
        <div className="flex justify-between items-center mb-1.5">
          <label className="flex items-center gap-1.5 text-xs font-bold text-slate-700">
            <FileText className="w-3.5 h-3.5 text-violet-600" />
            Mô tả quy trình nghiệp vụ & Báo cáo BI yêu cầu
          </label>
          <span className="text-[11px] text-slate-400 flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-amber-500" /> AI sẽ tự động phân tích Grain & Fact/Dim
          </span>
        </div>

        <textarea
          rows={2}
          className="w-full px-3.5 py-2.5 border border-slate-200 rounded-xl text-xs bg-slate-50/50 text-slate-800 outline-none focus:border-blue-500 focus:bg-white focus:ring-3 focus:ring-blue-500/10 transition resize-none leading-relaxed"
          placeholder="Nhập mô tả quy trình chuyến đi, quản lý tài xế, chương trình khuyến mãi và các chỉ số KPI cần theo dõi..."
          value={description}
          onChange={(e) => onDescriptionChange(e.target.value)}
        />

        {/* Suggestion Chips */}
        <div className="flex flex-wrap gap-1.5 mt-2">
          <span className="text-[11px] text-slate-400 font-semibold py-0.5">Gợi ý nhanh:</span>
          {PROMPT_SUGGESTIONS.map((chip, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                const newDesc = description ? `${description} ${chip}` : chip;
                onDescriptionChange(newDesc);
              }}
              className="text-[11px] px-2.5 py-0.5 rounded-full bg-slate-100/90 text-slate-600 border border-slate-200/80 hover:bg-blue-50 hover:text-blue-600 hover:border-blue-200 transition cursor-pointer"
            >
              + {chip}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

