import { MessageSquarePlus, Pencil } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import type { ProjectSessionResponse } from "@/api";
import { Button } from "@/common/components/ui/button";
import { Input } from "@/common/components/ui/input";
import {
  NativeSelect,
  NativeSelectOption,
} from "@/common/components/ui/native-select";

export function AgentSessionControls(props: {
  sessions: ProjectSessionResponse[];
  selectedSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewSession: () => void;
  onRenameSession: (title: string) => void;
}) {
  const { t } = useTranslation("ai-chat");
  const selected = props.sessions.find(
    (item) => item.id === props.selectedSessionId,
  );
  const [title, setTitle] = useState<string | null>(null);
  if (title !== null)
    return (
      <form
        className="flex items-center gap-1.5 border-b border-slate-800/80 bg-slate-900/40 p-2"
        onSubmit={(event) => {
          event.preventDefault();
          props.onRenameSession(title);
          setTitle(null);
        }}
      >
        <Input
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          autoFocus
          maxLength={255}
          className="h-8 border-slate-700 bg-slate-900 text-xs text-slate-100 placeholder:text-slate-500 focus-visible:ring-sky-500"
        />
        <Button
          type="submit"
          size="sm"
          className="h-8 shrink-0 bg-sky-600 px-3 text-xs font-semibold text-white hover:bg-sky-500"
        >
          {t("BTN_SAVE_SESSION_NAME")}
        </Button>
      </form>
    );
  return (
    <div className="flex items-center gap-1.5 border-b border-amber-200/80 bg-amber-100/30 p-2 dark:border-slate-800/80 dark:bg-slate-900/40">
      <div className="min-w-0 flex-1">
        <NativeSelect
          value={props.selectedSessionId ?? ""}
          onChange={(event) => props.onSelectSession(event.target.value)}
          aria-label={t("TXT_SESSION_LIST")}
          className="w-full"
          selectClassName="h-8 border-amber-200 bg-white px-2.5 text-xs text-slate-800 focus-visible:border-amber-500 focus-visible:ring-1 focus-visible:ring-amber-500/50 dark:border-slate-700/80 dark:bg-slate-900 dark:text-slate-200 dark:focus-visible:border-sky-500 dark:focus-visible:ring-sky-500/50"
        >
          <NativeSelectOption value="" disabled className="bg-white text-slate-400 dark:bg-slate-900 dark:text-slate-400">
            {t("TXT_SELECT_SESSION")}
          </NativeSelectOption>
          {props.sessions.map((session) => (
            <NativeSelectOption key={session.id} value={session.id} className="bg-white text-slate-800 dark:bg-slate-900 dark:text-slate-200">
              {session.title}
            </NativeSelectOption>
          ))}
        </NativeSelect>
      </div>
      {selected && (
        <Button
          size="icon-xs"
          variant="ghost"
          className="size-8 shrink-0 text-slate-600 hover:bg-amber-200/60 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-200"
          onClick={() => setTitle(selected.title)}
          aria-label={t("BTN_RENAME_SESSION")}
        >
          <Pencil className="size-3.5" />
        </Button>
      )}
      <Button
        size="sm"
        variant="secondary"
        onClick={props.onNewSession}
        className="h-8 shrink-0 gap-1.5 border border-amber-300 bg-amber-500 px-2.5 text-xs font-semibold text-white shadow-xs hover:bg-amber-600 dark:border-slate-700/80 dark:bg-slate-800/90 dark:text-slate-200 dark:hover:bg-slate-700 dark:hover:text-white"
      >
        <MessageSquarePlus className="size-3.5 text-amber-100 dark:text-sky-400" />
        <span>{t("BTN_NEW_SESSION")}</span>
      </Button>
    </div>
  );
}
