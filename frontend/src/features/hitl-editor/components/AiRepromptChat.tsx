/**
 * Presentation Component: Khung Chatbot AI Agent Re-prompting theo từng bảng
 * Trò chuyện tương tác với AI Agent kèm chip gợi ý nhanh & message bubbles
 */

import React from 'react';
import { ChatMessage } from '../types/hitl.types';
import { Send, Bot, User, Sparkles, Loader2 } from 'lucide-react';

export interface AiRepromptChatProps {
  messages: ChatMessage[];
  inputText: string;
  onInputChange: (text: string) => void;
  onSendMessage: () => void;
  isSending: boolean;
}

const CHAT_SUGGESTIONS = [
  '➕ Thêm cột updated_at TIMESTAMP',
  '💰 Đổi fare_amount thành DECIMAL(12,2)',
  '🔑 Tự động đặt driver_id làm Foreign Key',
];

export const AiRepromptChat: React.FC<AiRepromptChatProps> = ({
  messages,
  inputText,
  onInputChange,
  onSendMessage,
  isSending,
}) => {
  return (
    <div className="flex flex-col flex-1 overflow-hidden bg-white">
      {/* Chat Messages Area */}
      <div className="flex-1 flex flex-col gap-3 p-3.5 overflow-y-auto bg-slate-50/60 dark-scrollbar">
        {messages.map((msg) => {
          const isAi = msg.sender === 'ai';
          return (
            <div
              key={msg.id}
              className={`flex items-start gap-2 max-w-[90%] ${
                isAi ? 'self-start' : 'self-end flex-row-reverse'
              }`}
            >
              {/* Avatar Icon */}
              <div
                className={`w-6 h-6 rounded-full flex items-center justify-center text-xs flex-shrink-0 mt-0.5 ${
                  isAi
                    ? 'bg-blue-600 text-white shadow-xs'
                    : 'bg-indigo-600 text-white shadow-xs'
                }`}
              >
                {isAi ? <Bot className="w-3.5 h-3.5" /> : <User className="w-3.5 h-3.5" />}
              </div>

              {/* Message Content */}
              <div
                className={`p-3 text-xs leading-relaxed rounded-2xl shadow-2xs ${
                  isAi
                    ? 'bg-white text-slate-800 border border-slate-200/80 rounded-tl-xs'
                    : 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-medium rounded-tr-xs'
                }`}
              >
                {msg.text}
              </div>
            </div>
          );
        })}

        {isSending && (
          <div className="flex items-center gap-2 text-xs text-slate-400 bg-white p-2.5 rounded-xl border border-slate-200/80 w-fit">
            <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-600" />
            <span>AI Agent đang phân tích & cập nhật schema...</span>
          </div>
        )}
      </div>

      {/* Suggestion Chips */}
      <div className="px-3 py-1.5 bg-slate-100/70 border-t border-slate-200/60 flex items-center gap-1.5 overflow-x-auto dark-scrollbar">
        <Sparkles className="w-3 h-3 text-amber-500 flex-shrink-0" />
        <span className="text-[10px] text-slate-400 font-bold flex-shrink-0">Gợi ý:</span>
        {CHAT_SUGGESTIONS.map((chip, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => {
              onInputChange(chip);
            }}
            className="text-[10px] px-2 py-0.5 rounded-full bg-white text-slate-600 border border-slate-200 hover:bg-blue-50 hover:text-blue-600 hover:border-blue-200 transition whitespace-nowrap cursor-pointer"
          >
            {chip}
          </button>
        ))}
      </div>

      {/* Input Form Bar */}
      <div className="flex items-center gap-2 p-2.5 border-t border-slate-200 bg-white">
        <input
          type="text"
          className="flex-1 px-3 py-2 border border-slate-200 rounded-xl outline-none text-xs text-slate-800 bg-slate-50 focus:bg-white focus:border-blue-500 transition"
          placeholder="Nhập yêu cầu sửa đổi cho bảng này..."
          value={inputText}
          onChange={(e) => onInputChange(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !isSending && onSendMessage()}
        />
        <button
          onClick={onSendMessage}
          disabled={isSending || !inputText.trim()}
          className="px-3.5 py-2 text-xs font-bold rounded-xl border-none text-white cursor-pointer transition disabled:opacity-50 flex items-center gap-1 bg-blue-600 hover:bg-blue-700 shadow-xs"
        >
          <Send className="w-3.5 h-3.5" />
          Gửi
        </button>
      </div>
    </div>
  );
};

