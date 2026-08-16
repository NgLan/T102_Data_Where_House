/**
 * Presentation Component: Trạng thái PII Masking (FR6.2)
 *
 * Đây là chỉ báo CHỈ ĐỌC, không phải công tắc. Che thông tin cá nhân là biện pháp bảo mật
 * bắt buộc nên được bật cứng ở phía máy chủ qua biến môi trường `PII_MASKING_ENABLED`,
 * không cho phép tắt bằng một cú click trên giao diện.
 */

import React from 'react';
import { ShieldCheck, Lock } from 'lucide-react';

export const MaskingToggle: React.FC = () => {
  return (
    <div className="flex items-center justify-between mt-4 p-3 bg-slate-50/90 border border-slate-200/80 rounded-xl">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg flex items-center justify-center bg-indigo-100 text-indigo-600">
          <ShieldCheck className="w-4 h-4" />
        </div>

        <div>
          <span className="text-xs font-bold text-slate-800 m-0 select-none block">
            Tự động phát hiện &amp; Che chắn dữ liệu nhạy cảm (PII Masking &amp; Anonymization)
          </span>
          <span className="text-[11px] text-slate-400">
            Tự động ẩn Email, SĐT, CCCD &amp; Thẻ ngân hàng trước khi gửi schema sang AI Agent
          </span>
        </div>
      </div>

      {/* Chỉ báo trạng thái — luôn bật, do quản trị hệ thống cấu hình */}
      <div className="flex items-center gap-2">
        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-600 border border-indigo-200">
          PROTECTED
        </span>
        <span
          title="Luôn bật — cấu hình bởi quản trị hệ thống"
          className="flex items-center gap-1 text-[10px] font-semibold text-slate-400 bg-slate-100 border border-slate-200 px-2 py-0.5 rounded-full"
        >
          <Lock className="w-3 h-3" /> Luôn bật
        </span>
      </div>
    </div>
  );
};
