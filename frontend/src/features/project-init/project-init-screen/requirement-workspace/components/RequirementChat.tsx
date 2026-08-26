"use client";

import { Bot, X } from "lucide-react";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import type {
  AnswerRequirementClarificationRequest,
  ClarificationQuestionResponse,
  RequirementClarificationStatus,
  RequirementContinuationState,
  SessionEventResponse,
} from "@/api";
import { Button } from "@/common/components/ui/button";
import { RequirementChatInput } from "./requirement-chat/RequirementChatInput";
import { RequirementChatMessages } from "./requirement-chat/RequirementChatMessages";
import { RequirementClarificationQuestion } from "./requirement-chat/RequirementClarificationQuestion";

interface RequirementChatProps {
  isOpen: boolean;
  onOpenChange: (isOpen: boolean) => void;
  status: RequirementClarificationStatus;
  continuationState: RequirementContinuationState;
  events: SessionEventResponse[];
  pending: ClarificationQuestionResponse | null;
  canAnswer: boolean;
  isSending: boolean;
  hasError: boolean;
  onAnswer: (answer: AnswerRequirementClarificationRequest) => Promise<unknown>;
  onMessage: (message: string) => Promise<unknown>;
  onContinueEditing: () => Promise<unknown>;
  onContinueAnalysis: () => Promise<void>;
}

/**
 * Floating bot drawer điều phối hội thoại làm rõ yêu cầu giữa người dùng và Agent.
 *
 * @param props - Thuộc tính trạng thái phiên chat, danh sách sự kiện và hàm phản hồi
 * @returns Floating action button và drawer hội thoại
 */
export function RequirementChat(props: RequirementChatProps) {
  const { t } = useTranslation("project-init");
  const { continuationState, onOpenChange, pending } = props;
  const [lastAnswer, setLastAnswer] = useState<AnswerRequirementClarificationRequest>();
  const [lastMessage, setLastMessage] = useState<string>();

  useEffect(() => {
    if (pending || continuationState === "AWAITING_DECISION") {
      onOpenChange(true);
    }
  }, [pending, continuationState, onOpenChange]);

  const handleSubmit = async (payload: AnswerRequirementClarificationRequest) => {
    setLastAnswer(payload);
    await props.onAnswer(payload);
  };
  const handleMessage = async (message: string) => {
    setLastMessage(message);
    await props.onMessage(message);
  };

  if (!props.isOpen) {
    return null;
  }

  return (
    <aside className="fixed inset-0 z-50 flex flex-col border-l bg-background shadow-2xl lg:sticky lg:top-4 lg:z-20 lg:h-[calc(100vh-8rem)] lg:w-96 lg:rounded-xl lg:border">
          <header className="flex items-center justify-between border-b p-4">
            <div>
              <h2 className="font-semibold text-foreground">{t("TXT_REQUIREMENT_CHAT_TITLE")}</h2>
              <p className="text-xs text-muted-foreground">{t(`TXT_BOT_${props.status}`)}</p>
            </div>
            <Button
              type="button"
              size="icon"
              variant="ghost"
              className="cursor-pointer"
              onClick={() => props.onOpenChange(false)}
            >
              <X className="size-4" />
            </Button>
          </header>

          <RequirementChatMessages events={props.events} isSending={props.isSending} />

          <footer className="space-y-3 border-t bg-card/40 p-4">
            {props.continuationState === "AWAITING_DECISION" && props.canAnswer && (
              <div className="grid grid-cols-2 gap-2">
                <Button type="button" onClick={() => void props.onContinueAnalysis()}
                  disabled={props.isSending}>{t("BTN_CONTINUE_ANALYSIS")}</Button>
                <Button type="button" variant="outline"
                  disabled={props.isSending}
                  onClick={() => void props.onContinueEditing()}>
                  {t("BTN_CONTINUE_EDITING")}
                </Button>
              </div>
            )}
            {props.continuationState === "AWAITING_DECISION" ? null : props.pending ? (
              <RequirementClarificationQuestion
                key={props.pending.question}
                pending={props.pending}
                canAnswer={props.canAnswer}
                isSending={props.isSending}
                onSubmit={handleSubmit}
              />
            ) : (
              <RequirementChatInput
                canAnswer={props.canAnswer && props.status !== "IDLE" && !props.isSending}
                isSending={props.isSending}
                onSubmit={handleMessage}
              />
            )}

            {props.canAnswer && props.hasError && props.pending && lastAnswer && (
              <Button
                type="button"
                size="sm"
                variant="destructive"
                className="w-full cursor-pointer"
                onClick={() => void handleSubmit(lastAnswer)}
              >
                {t("BTN_RETRY_SEND")}
              </Button>
            )}
            {props.canAnswer && props.hasError && !props.pending && lastMessage && (
              <Button type="button" size="sm" variant="destructive"
                className="w-full cursor-pointer"
                onClick={() => void handleMessage(lastMessage)}>
                {t("BTN_RETRY_SEND")}
              </Button>
            )}
          </footer>
        </aside>
  );
}
