/**
 * Custom Hook quản lý khung chat yêu cầu AI chỉnh sửa mô hình dữ liệu (UC6 / T-024)
 */

import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useProjectStore } from '@/common/stores/useProjectStore';
import { reviseDataModelWithAiApi } from '../services/hitl-api';
import { ChatMessage } from '../types/hitl.types';

/** Sinh nhãn thời gian hiển thị cạnh mỗi tin nhắn */
function nowLabel(): string {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

/** Tạo một tin nhắn mới trong khung chat */
function buildMessage(sender: ChatMessage['sender'], text: string): ChatMessage {
  return { id: `${sender}_${Date.now()}_${Math.random()}`, sender, text, timestamp: nowLabel() };
}

export interface UseAiRepromptOptions {
  /** Gọi lại sau khi AI tạo xong đề xuất, để khung so sánh khác biệt nạp lại dữ liệu mới */
  onProposalCreated?: () => void | Promise<void>;
}

export function useAiReprompt(options: UseAiRepromptOptions = {}) {
  const { t } = useTranslation('hitlEditor');
  const { t: tErrors } = useTranslation('errors');
  const dataModel = useProjectStore((state) => state.dataModel);

  const [messages, setMessages] = useState<ChatMessage[]>([
    buildMessage('ai', t('chat.greeting')),
  ]);
  const [inputText, setInputText] = useState<string>('');
  const [isSending, setIsSending] = useState<boolean>(false);

  /**
   * Gửi yêu cầu chỉnh sửa cho AI Agent và hiển thị lời giải thích trả về trong khung chat.
   */
  const handleSendMessage = async (): Promise<void> => {
    const instruction = inputText.trim();
    if (!instruction || isSending) return;

    if (!dataModel) {
      setMessages((prev) => [...prev, buildMessage('ai', tErrors('DATA_MODEL_NOT_FOUND'))]);
      return;
    }

    setMessages((prev) => [...prev, buildMessage('user', instruction)]);
    setInputText('');
    setIsSending(true);

    try {
      const proposal = await reviseDataModelWithAiApi(dataModel.id, instruction);
      setMessages((prev) => [
        ...prev,
        buildMessage('ai', proposal.summary || t('chat.proposal_created')),
      ]);
      await options.onProposalCreated?.();
    } catch (error) {
      const errorCode = (error as { error_code?: string })?.error_code ?? 'UNKNOWN_ERROR';
      setMessages((prev) => [
        ...prev,
        buildMessage('ai', tErrors(errorCode, { defaultValue: tErrors('UNKNOWN_ERROR') })),
      ]);
    } finally {
      setIsSending(false);
    }
  };

  return {
    messages,
    inputText,
    setInputText,
    isSending,
    handleSendMessage,
  };
}
