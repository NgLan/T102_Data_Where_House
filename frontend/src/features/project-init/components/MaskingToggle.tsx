/**
 * Presentation Component: Toggle PII Masking
 * Modern switch toggle với icon Bảo mật Shield & status pill
 */

import React from 'react';
import { ShieldCheck, Lock } from 'lucide-react';

export interface MaskingToggleProps {
  isEnabled: boolean;
  onChange: (val: boolean) => void;
}

export const MaskingToggle: React.FC<MaskingToggleProps> = ({ isEnabled, onChange }) => {
  return (
    <div className="flex items-center justify-between mt-4 p-3 bg-slate-50/90 border border-slate-200/80 rounded-xl">
      <div className="flex items-center gap-3">
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center transition-colors ${
          isEnabled ? 'bg-indigo-100 text-indigo-600' : 'bg-slate-200 text-slate-400'
        }`}>
          <ShieldCheck className="w-4 h-4" />
        </div>

        <div>
          <label htmlFor="masking" className="cursor-pointer text-xs font-bold text-slate-800 m-0 select-none block">
            Tự động phát hiện & Che chắn dữ liệu nhạy cảm (PII Masking & Anonymization)
          </label>
          <span className="text-[11px] text-slate-400">
            Tự động ẩn Email, SĐT, CCCD & Thẻ ngân hàng trước khi AI Agent xử lý schema
          </span>
        </div>
      </div>

      {/* Switch Toggle */}
      <div className="flex items-center gap-2">
        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
          isEnabled ? 'bg-indigo-50 text-indigo-600 border border-indigo-200' : 'bg-slate-200 text-slate-500'
        }`}>
          {isEnabled ? 'PROTECTED' : 'OFF'}
        </span>

        <button
          type="button"
          role="switch"
          aria-checked={isEnabled}
          onClick={() => onChange(!isEnabled)}
          className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
            isEnabled ? 'bg-indigo-600' : 'bg-slate-300'
          }`}
        >
          <span
            className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-md ring-0 transition duration-200 ease-in-out ${
              isEnabled ? 'translate-x-5' : 'translate-x-0'
            }`}
          />
        </button>
      </div>
    </div>
  );
};

