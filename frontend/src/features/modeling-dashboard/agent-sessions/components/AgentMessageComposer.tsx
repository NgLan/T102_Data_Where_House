import { Loader2, SendHorizonal } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import { Textarea } from "@/common/components/ui/textarea";

export function AgentMessageComposer(props: {
  draft: string;
  canSend: boolean;
  isSending: boolean;
  hasSession: boolean;
  isClarificationPending: boolean;
  onDraftChange: (value: string) => void;
  onSend: () => void;
}) {
  const { t } = useTranslation("ai-chat");
  return (
    <div className="border-t border-amber-200/80 bg-amber-100/30 p-3 dark:border-slate-800/80 dark:bg-slate-900/40">
      <div className="relative">
        <Textarea
          value={props.draft}
          onChange={(event) => props.onDraftChange(event.target.value)}
          disabled={
            !props.hasSession || props.isSending || props.isClarificationPending
          }
          placeholder={
            props.isClarificationPending
              ? t("TXT_ANSWER_CLARIFICATION_FIRST")
              : props.hasSession
              ? t("AI_CHAT_INPUT_PLACEHOLDER")
              : t("TXT_CREATE_SESSION_FIRST")
          }
          className="h-22 resize-none rounded-xl border-amber-200/90 bg-white pb-10 text-xs leading-relaxed text-slate-900 placeholder:text-slate-400 focus-visible:border-amber-500 focus-visible:ring-1 focus-visible:ring-amber-500/50 dark:border-slate-700/70 dark:bg-slate-900/90 dark:text-slate-100 dark:placeholder:text-slate-500 dark:focus-visible:border-sky-500 dark:focus-visible:ring-sky-500/50"
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey && props.canSend) {
              event.preventDefault();
              props.onSend();
            }
          }}
        />
        <Button
          className="absolute bottom-2 right-2 size-7.5 rounded-lg bg-amber-500 text-white shadow-sm hover:bg-amber-600 disabled:opacity-30 disabled:hover:bg-amber-500 dark:bg-sky-600 dark:hover:bg-sky-500 dark:disabled:hover:bg-sky-600 transition-colors"
          size="icon"
          disabled={!props.canSend}
          onClick={props.onSend}
          aria-label={t("BTN_AI_CHAT_SEND")}
        >
          {props.isSending ? (
            <Loader2 className="size-3.5 animate-spin" />
          ) : (
            <SendHorizonal className="size-3.5" />
          )}
        </Button>
      </div>
    </div>
  );
}
