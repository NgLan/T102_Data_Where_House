"use client";

import { Loader2, SendHorizonal } from "lucide-react";
import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import type {
  AnswerClarificationRequest,
  ClarificationQuestionResponse,
} from "@/api";
import { Button } from "@/common/components/ui/button";
import { Textarea } from "@/common/components/ui/textarea";
import { cn } from "@/common/lib/utils";
import { createClarificationAnswerSchema } from "../schemas/clarification-answer-schema";

interface AgentClarificationCardProps {
  clarification: ClarificationQuestionResponse;
  isSubmitting: boolean;
  onSubmit: (answer: AnswerClarificationRequest) => void;
}

/** Form trả lời đúng clarification hiện đang pending. */
export function AgentClarificationCard(props: AgentClarificationCardProps) {
  const { t } = useTranslation("ai-chat");
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [isCustom, setIsCustom] = useState(false);
  const [customAnswer, setCustomAnswer] = useState("");
  const schema = useMemo(
    () => createClarificationAnswerSchema(t("MSG_CLARIFICATION_ANSWER_REQUIRED")),
    [t],
  );
  const answer: AnswerClarificationRequest = isCustom
    ? { answer_type: "custom", custom_answer: customAnswer }
    : { answer_type: "option", option_index: selectedIndex };
  const validation = schema.safeParse(answer);

  const handleSubmit = () => {
    if (validation.success && !props.isSubmitting) props.onSubmit(validation.data);
  };

  return (
    <form
      className="mx-3 mb-3 space-y-3 rounded-xl border border-amber-300 bg-amber-50 p-3 dark:border-sky-700/70 dark:bg-sky-950/30"
      onSubmit={(event) => {
        event.preventDefault();
        handleSubmit();
      }}
    >
      <fieldset disabled={props.isSubmitting} className="space-y-2">
        <legend className="text-xs font-semibold text-slate-900 dark:text-slate-100">
          {props.clarification.question}
        </legend>
        {props.clarification.reason && (
          <p className="text-[11px] text-slate-500 dark:text-slate-400">
            {props.clarification.reason}
          </p>
        )}
        <div className="grid gap-2">
          {props.clarification.options.map((option, index) => (
            <ChoiceButton
              key={`${index}-${option}`}
              isSelected={!isCustom && selectedIndex === index}
              label={option}
              onClick={() => {
                setIsCustom(false);
                setSelectedIndex(index);
              }}
            />
          ))}
          <ChoiceButton
            isSelected={isCustom}
            label={t("TXT_CLARIFICATION_OTHER")}
            onClick={() => setIsCustom(true)}
          />
        </div>
        {isCustom && (
          <div className="space-y-1">
            <Textarea
              value={customAnswer}
              onChange={(event) => setCustomAnswer(event.target.value)}
              placeholder={t("CLARIFICATION_CUSTOM_PLACEHOLDER")}
              maxLength={2000}
              className="min-h-20 resize-none bg-white dark:bg-slate-900"
            />
            {!customAnswer.trim() && (
              <p className="text-[11px] text-destructive">
                {t("MSG_CLARIFICATION_ANSWER_REQUIRED")}
              </p>
            )}
          </div>
        )}
      </fieldset>
      <Button
        type="submit"
        size="sm"
        disabled={!validation.success || props.isSubmitting}
        className="cursor-pointer"
      >
        {props.isSubmitting ? (
          <Loader2 className="size-3.5 animate-spin" />
        ) : (
          <SendHorizonal className="size-3.5" />
        )}
        {t("BTN_SUBMIT_CLARIFICATION")}
      </Button>
    </form>
  );
}

function ChoiceButton(props: {
  isSelected: boolean;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={props.onClick}
      className={cn(
        "cursor-pointer rounded-lg border px-3 py-2 text-left text-xs transition-colors hover:border-amber-500 hover:bg-amber-100 dark:hover:border-sky-500 dark:hover:bg-sky-950",
        props.isSelected && "border-amber-500 bg-amber-100 dark:border-sky-500 dark:bg-sky-950",
      )}
    >
      {props.label}
    </button>
  );
}
