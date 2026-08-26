"use client";

import { Send } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import { Textarea } from "@/common/components/ui/textarea";

interface RequirementChatInputProps {
  canAnswer: boolean;
  isSending: boolean;
  onSubmit: (message: string) => Promise<void>;
}

/**
 * Ô nhập tin nhắn tự do gửi đến Agent trong phiên làm rõ yêu cầu.
 *
 * @param props - Quyền trả lời, cờ đang gửi và hàm gửi câu trả lời
 * @returns Khung nhập tin nhắn textarea
 */
export function RequirementChatInput(props: RequirementChatInputProps) {
  const { t } = useTranslation("project-init");
  const [message, setMessage] = useState("");

  const handleSend = () => {
    const trimmed = message.trim();
    if (trimmed) {
      void props.onSubmit(trimmed);
      setMessage("");
    }
  };

  return (
    <div className="relative w-full">
      <Textarea
        value={message}
        disabled={!props.canAnswer || props.isSending}
        className="min-h-20 w-full resize-none rounded-xl pr-12 pb-3 text-sm focus-visible:ring-1"
        placeholder={t("TXT_REQUIREMENT_CHAT_PLACEHOLDER")}
        onChange={(event) => setMessage(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            handleSend();
          }
        }}
      />
      <Button
        type="button"
        size="icon"
        className="absolute bottom-2.5 right-2.5 size-7 cursor-pointer rounded-lg"
        disabled={!props.canAnswer || props.isSending || !message.trim()}
        onClick={handleSend}
      >
        <Send className="size-3.5" />
      </Button>
    </div>
  );
}
