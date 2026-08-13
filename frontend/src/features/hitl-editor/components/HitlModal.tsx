/**
 * Presentation Component: HITL Modal Pop-up tinh chỉnh bảng
 * Backdrop blur overlay & rounded glass dialog với Attribute Grid + AI Chat
 */

import React from 'react';
import { useProjectStore } from '@/common/stores/useProjectStore';
import { useHitlEditor } from '../hooks/useHitlEditor';
import { useAiReprompt } from '../hooks/useAiReprompt';
import { AttributeDataGrid } from './AttributeDataGrid';
import { AiRepromptChat } from './AiRepromptChat';
import { ProposalReviewActions } from './ProposalReviewActions';
import { Edit3, X, Sparkles, TableProperties, Bot } from 'lucide-react';

export const HitlModal: React.FC = () => {
  const isHitlModalOpen = useProjectStore((state) => state.isHitlModalOpen);
  const activeTableName = useProjectStore((state) => state.activeTableName);
  const closeHitlModal = useProjectStore((state) => state.closeHitlModal);

  const { columns, handleAddColumn, handleUpdateColumn, handleDeleteColumn } = useHitlEditor(activeTableName);
  const { messages, inputText, setInputText, isSending, handleSendMessage } = useAiReprompt();

  if (!isHitlModalOpen) return null;

  return (
    /* Backdrop Overlay */
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 backdrop-blur-md p-4 screen-animate">
      {/* Modal Dialog Container */}
      <div className="flex flex-col w-[960px] max-w-[95vw] h-[660px] max-h-[90vh] bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden">
        {/* Header */}
        <div className="flex justify-between items-center bg-slate-50/90 px-6 py-4 border-b border-slate-200/80">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-blue-100/80 text-blue-600 flex items-center justify-center font-bold">
              <Edit3 className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-base font-bold text-slate-900">
                  HITL Editor: Tinh chỉnh Bảng
                </span>
                <span className="text-xs font-mono font-bold px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-700 border border-blue-200">
                  {activeTableName || 'Fact_Rides'}
                </span>
              </div>
              <p className="text-xs text-slate-400 m-0">Human-In-The-Loop schema refinement & AI Agent re-prompting</p>
            </div>
          </div>

          <button
            onClick={closeHitlModal}
            className="w-8 h-8 rounded-full bg-slate-200/60 hover:bg-slate-200 text-slate-500 hover:text-slate-800 flex items-center justify-center transition cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body Split View */}
        <div className="flex flex-1 gap-4 p-5 overflow-hidden bg-slate-50/40">
          {/* Left Side: Attribute Grid */}
          <div className="flex flex-col flex-[6] bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
            <AttributeDataGrid
              columns={columns}
              onAddColumn={handleAddColumn}
              onUpdateColumn={handleUpdateColumn}
              onDeleteColumn={handleDeleteColumn}
            />
          </div>

          {/* Right Side: AI Re-prompt Chat Panel */}
          <div className="flex flex-col flex-[4] bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
            <div className="bg-slate-50/90 px-3.5 py-2.5 border-b border-slate-200/80 flex items-center gap-2 text-xs font-bold text-slate-800">
              <Bot className="w-4 h-4 text-blue-600" />
              <span>Trợ lý AI Agent (Re-prompting Bảng)</span>
            </div>

            <AiRepromptChat
              messages={messages}
              inputText={inputText}
              onInputChange={setInputText}
              onSendMessage={handleSendMessage}
              isSending={isSending}
            />
          </div>
        </div>

        {/* Footer Actions */}
        <ProposalReviewActions
          onAccept={() => {
            alert(`Đã áp dụng thay đổi thành công vào ${activeTableName}!`);
            closeHitlModal();
          }}
          onReject={closeHitlModal}
          onRetry={() => alert('Đã gửi yêu cầu tạo lại đề xuất cho AI!')}
        />
      </div>
    </div>
  );
};

