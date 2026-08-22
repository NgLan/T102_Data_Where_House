import { Loader2, SendHorizonal } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import { Textarea } from "@/common/components/ui/textarea";

export function AgentMessageComposer(props: {
  draft: string;
  canSend: boolean;
  isSending: boolean;
  hasSession: boolean;
  onDraftChange: (value: string) => void;
  onSend: () => void;
}) {
  const { t } = useTranslation("ai-chat");
  return (
    <div className="border-t border-slate-800/80 bg-slate-900/40 p-3">
      <div className="relative">
        <Textarea
          value={props.draft}
          onChange={(event) => props.onDraftChange(event.target.value)}
          disabled={!props.hasSession || props.isSending}
          placeholder={
            props.hasSession
              ? t("AI_CHAT_INPUT_PLACEHOLDER")
              : t("TXT_CREATE_SESSION_FIRST")
          }
          className="h-22 resize-none rounded-xl border-slate-700/70 bg-slate-900/90 pb-10 text-xs leading-relaxed text-slate-100 placeholder:text-slate-500 focus-visible:border-sky-500 focus-visible:ring-1 focus-visible:ring-sky-500/50"
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey && props.canSend) {
              event.preventDefault();
              props.onSend();
            }
          }}
        />
        <Button
          className="absolute bottom-2 right-2 size-7.5 rounded-lg bg-sky-600 text-white shadow-sm hover:bg-sky-500 disabled:opacity-30 disabled:hover:bg-sky-600 transition-colors"
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
