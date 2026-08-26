"use client";

import { Bot, Send } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import type { AnswerRequirementClarificationRequest, ClarificationQuestionResponse } from "@/api";
import { Button } from "@/common/components/ui/button";

interface RequirementClarificationQuestionProps {
  pending: ClarificationQuestionResponse;
  canAnswer: boolean;
  isSending: boolean;
  onSubmit: (answer: AnswerRequirementClarificationRequest) => Promise<void>;
}

/**
 * Khối hiển thị câu hỏi làm rõ từ Agent kèm các lựa chọn có sẵn và ô nhập tùy biến.
 *
 * @param props - Dữ liệu câu hỏi, quyền trả lời, trạng thái gửi và hàm callback
 * @returns Khung câu hỏi làm rõ tương tác
 */
export function RequirementClarificationQuestion(props: RequirementClarificationQuestionProps) {
  const { t } = useTranslation("project-init");
  const [customAnswer, setCustomAnswer] = useState("");

  const handleSelectOption = (index: number) => {
    void props.onSubmit({ answer_type: "option", option_index: index });
  };

  const handleSendCustom = () => {
    const trimmed = customAnswer.trim();
    if (trimmed) {
      void props.onSubmit({ answer_type: "custom", custom_answer: trimmed });
    }
  };

  return (
    <div className="space-y-2.5">
      <div className="rounded-xl border border-amber-300 bg-amber-50/80 p-3 shadow-xs dark:border-amber-700/60 dark:bg-amber-950/30">
        <div className="mb-1 flex items-center gap-1.5 text-xs font-semibold text-amber-900 dark:text-amber-200">
          <Bot className="size-3.5 text-amber-600 dark:text-amber-400" />
          <span>{t("TXT_BOT_NEEDS_CLARIFICATION")}</span>
        </div>
        <p className="text-sm font-semibold leading-snug text-foreground">{props.pending.question}</p>
        {props.pending.reason && (
          <p className="mt-1.5 text-xs leading-normal text-muted-foreground">{props.pending.reason}</p>
        )}
      </div>

      <div className="flex max-h-60 flex-col gap-2 overflow-y-auto pr-1">
        {props.pending.options.map((option, index) => (
          <Button
            key={`${index}-${option}`}
            type="button"
            variant="outline"
            disabled={!props.canAnswer || props.isSending}
            onClick={() => handleSelectOption(index)}
            className="flex h-auto w-full cursor-pointer items-start justify-start gap-2.5 whitespace-normal break-words rounded-xl border bg-card p-3 text-left text-sm font-normal text-card-foreground shadow-xs transition-colors hover:border-primary/50 hover:bg-accent active:scale-[0.99]"
          >
            <span className="mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary">
              {index + 1}
            </span>
            <span className="flex-1 leading-snug">{option}</span>
          </Button>
        ))}

        <div className="relative flex w-full items-center gap-2.5 rounded-xl border border-dashed border-primary/40 bg-card p-2.5 shadow-xs transition-all focus-within:border-primary focus-within:ring-1 focus-within:ring-primary/20">
          <span className="ml-0.5 flex size-5 shrink-0 items-center justify-center rounded-full bg-muted text-xs font-semibold text-muted-foreground">
            {props.pending.options.length + 1}
          </span>
          <input
            type="text"
            value={customAnswer}
            disabled={!props.canAnswer || props.isSending}
            placeholder={t("TXT_CLARIFICATION_OTHER_PLACEHOLDER")}
            onChange={(event) => setCustomAnswer(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                event.preventDefault();
                handleSendCustom();
              }
            }}
            className="flex-1 bg-transparent pr-8 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none"
          />
          <Button
            type="button"
            size="icon"
            className="absolute right-1.5 size-7 cursor-pointer rounded-lg"
            disabled={!props.canAnswer || props.isSending || !customAnswer.trim()}
            onClick={handleSendCustom}
          >
            <Send className="size-3.5" />
          </Button>
        </div>
      </div>
    </div>
  );
}
