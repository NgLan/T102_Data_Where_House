/**
 * Pure Presentation Component: Nút bấm kích hoạt AI Agent phân tích
 * Style: Nút primary lớn theo wildframe
 */

import React from 'react';

export interface AnalyzeTriggerButtonProps {
  isAnalyzing: boolean;
  onClick: () => void;
}

export const AnalyzeTriggerButton: React.FC<AnalyzeTriggerButtonProps> = ({
  isAnalyzing,
  onClick,
}) => {
  return (
    <button
      onClick={onClick}
      disabled={isAnalyzing}
      className="w-full mt-1.5 py-3 px-4 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed text-white font-semibold text-[15px] rounded-lg border-none cursor-pointer transition-all duration-200 flex items-center justify-center gap-2 shadow-[0_2px_4px_rgba(37,99,235,0.2)] hover:translate-y-[-1px] hover:shadow-[0_4px_8px_rgba(37,99,235,0.3)]"
    >
      {isAnalyzing ? (
        <>
          <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          Đang phân tích dữ liệu...
        </>
      ) : (
        <>✨ AI Agents Phân tích & Tự động dựng Datawarehouse (ERD)</>
      )}
    </button>
  );
};
