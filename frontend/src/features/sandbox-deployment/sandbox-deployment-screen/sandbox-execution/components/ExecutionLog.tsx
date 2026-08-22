import { Terminal } from "lucide-react";
import { useTranslation } from "react-i18next";
import { useAppNotification } from "@/common/notifications";
import { cn } from "@/common/lib/utils";
import type { ExecutionLogEntry } from "../types/execution-log-types";

interface ExecutionLogProps {
  logs: readonly ExecutionLogEntry[];
}

/** Hiển thị execution log dưới dạng live region không giành focus. */
export function ExecutionLog({ logs }: ExecutionLogProps) {
  const { t } = useTranslation("sandbox-deployment");
  return (
    <section className="flex min-h-[220px] flex-1 flex-col">
      <ExecutionLogHeader />
      <div className="flex flex-1 flex-col overflow-hidden rounded-xl border border-slate-800 bg-slate-950 font-mono text-xs shadow-inner">
        <div className="border-b border-slate-800 px-3 py-1.5 text-right text-[10px] text-slate-400">
          {t("TXT_TERMINAL_HOST")}
        </div>
        <div className="dark-scrollbar min-h-[180px] flex-1 space-y-1 overflow-y-auto p-3" role="log" aria-live="polite">
          <ExecutionLogEntries logs={logs} />
        </div>
      </div>
    </section>
  );
}

function ExecutionLogHeader() {
  const { t } = useTranslation("sandbox-deployment");
  return (
    <header className="mb-1.5 flex items-center justify-between text-xs font-bold">
      <span className="flex items-center gap-1.5">
        <Terminal className="size-3.5 text-muted-foreground" aria-hidden="true" />
        {t("TXT_TERMINAL_LOG")}
      </span>
      <span className="font-mono text-[10px] font-normal text-muted-foreground">{t("TXT_TERMINAL_VERSION")}</span>
    </header>
  );
}

function ExecutionLogEntries({ logs }: ExecutionLogProps) {
  const { t } = useTranslation("sandbox-deployment");
  const { getErrorMessage } = useAppNotification();
  if (logs.length === 0) return <p className="text-slate-500">❯ {t("MSG_TERMINAL_READY")}</p>;
  return logs.map((log) => (
    <p key={log.id} className="flex items-start gap-1.5">
      <span className="select-none text-slate-600">❯</span>
      <span className="text-[10.5px] text-slate-500">[{log.timestamp}]</span>
      <span className={logClassName(log)}>
        {"errorCode" in log ? getErrorMessage(log.errorCode) : t(log.translationKey, log.params)}
      </span>
    </p>
  ));
}

function logClassName(log: ExecutionLogEntry): string {
  return cn(
    log.type === "error" && "font-semibold text-rose-400",
    log.type === "success" && "font-semibold text-emerald-400",
    log.type === "info" && "text-slate-300",
  );
}
