import { useTranslation } from "react-i18next";
import { Textarea } from "@/common/components/ui/textarea";
import type { DdlDialect } from "../../../constants/supported-ddl-dialects";
import { DdlEditorToolbar } from "./DdlEditorToolbar";

interface DdlEditorProps {
  ddlCode: string;
  dialect: DdlDialect;
  isRefreshing: boolean;
  onCopyDdl: () => void;
  onDdlCodeChange: (value: string) => void;
  onDialectChange: (value: DdlDialect) => void;
  onDownloadDocument: () => void;
  onDownloadSql: () => void;
  onFormatDdl: () => void;
}

/** Hiển thị DDL editor đơn giản bằng common Textarea. */
export function DdlEditor(props: DdlEditorProps) {
  const { t } = useTranslation("sandbox-deployment");
  const lineCount = props.ddlCode.split("\n").length;
  return (
    <section className="flex h-[520px] min-h-0 flex-[7] flex-col overflow-hidden rounded-2xl border border-slate-800 bg-slate-950 shadow-xl shadow-slate-950/20 lg:h-full">
      <DdlEditorToolbar
        dialect={props.dialect}
        isRefreshing={props.isRefreshing}
        onCopyDdl={props.onCopyDdl}
        onDialectChange={props.onDialectChange}
        onDownloadDocument={props.onDownloadDocument}
        onDownloadSql={props.onDownloadSql}
        onFormatDdl={props.onFormatDdl}
      />
      <Textarea
        value={props.ddlCode}
        disabled={props.isRefreshing}
        spellCheck={false}
        aria-label={t("DDL_EDITOR_LABEL")}
        onChange={(event) => props.onDdlCodeChange(event.target.value)}
        className="dark-scrollbar min-h-0 flex-1 overflow-y-auto resize-none rounded-none border-0 bg-slate-950 p-4 font-mono text-[13px] leading-relaxed text-sky-300 focus-visible:ring-0 [field-sizing:fixed]"
      />
      <DdlEditorFooter dialect={props.dialect} lineCount={lineCount} />
    </section>
  );
}

function DdlEditorFooter({
  dialect,
  lineCount,
}: {
  dialect: DdlDialect;
  lineCount: number;
}) {
  const { t } = useTranslation("sandbox-deployment");
  return (
    <footer className="flex items-center justify-between border-t border-slate-800/80 bg-slate-950/90 px-4 py-1.5 font-mono text-[10px] text-slate-500">
      <span>{t("TXT_EDITOR_STATS", { lines: lineCount })}</span>
      <span>{t("TXT_TARGET_DIALECT", { dialect: t(`TXT_DIALECT_${dialect}`) })}</span>
    </footer>
  );
}
