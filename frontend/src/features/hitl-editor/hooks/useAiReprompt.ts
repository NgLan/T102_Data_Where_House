/**
 * Custom Hook quản lý AI Re-prompting Chat trong HITL Modal
 */

import { useState } from 'react';
import { ChatMessage } from '../types/hitl.types';

const INITIAL_MESSAGES: ChatMessage[] = [
  {
    id: 'm1',
    sender: 'ai',
    text: 'Tui đang mở bảng này để hỗ trợ bạn chỉnh sửa. Bạn muốn thêm cột, đổi kiểu dữ liệu hay tách bảng phụ nào không?',
    timestamp: '08:30',
  },
];

export function useAiReprompt() {
  const [messages, setMessages] = useState<ChatMessage[]>(INITIAL_MESSAGES);
  const [inputText, setInputText] = useState<string>('');
  const [isSending, setIsSending] = useState<boolean>(false);

  const handleSendMessage = () => {
    if (!inputText.trim()) return;

    const userMsg: ChatMessage = {
      id: `usr_${Date.now()}`,
      sender: 'user',
      text: inputText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setIsSending(true);

    // Giả lập AI trả lời sau 600ms
    setTimeout(() => {
      const aiMsg: ChatMessage = {
        id: `ai_${Date.now()}`,
        sender: 'ai',
        text: 'Đã ghi nhận yêu cầu! Tôi đã đề xuất cập nhật lại kiểu dữ liệu và thêm chỉ mục Foreign Key.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, aiMsg]);
      setIsSending(false);
    }, 600);
  };

  return {
    messages,
    inputText,
    setInputText,
    isSending,
    handleSendMessage,
  };
}
