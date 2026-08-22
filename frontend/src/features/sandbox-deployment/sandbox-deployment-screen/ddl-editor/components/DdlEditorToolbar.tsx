import type { ReactNode } from "react";
import { Code2, Copy, Download, FileText, Loader2, Wand2 } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Badge } from "@/common/components/ui/badge";
import { Button } from "@/common/components/ui/button";
import {
  NativeSelect,
  NativeSelectOption,
} from "@/common/components/ui/native-select";
import {
  SUPPORTED_DDL_DIALECTS,
  isDdlDialect,
  type DdlDialect,
} from "../../../constants/supported-ddl-dialects";

interface DdlEditorToolbarProps {
  dialect: DdlDialect;
  isRefreshing: boolean;
  onCopyDdl: () => void;
  onDialectChange: (value: DdlDialect) => void;
  onDownloadDocument: () => void;
  onDownloadSql: () => void;
  onFormatDdl: () => void;
}

/** Hiển thị dialect selector và các command của DDL editor. */
export function DdlEditorToolbar(props: DdlEditorToolbarProps) {
  return (
    <header className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800/80 bg-slate-900/90 px-4 py-3 text-slate-200">
      <EditorIdentity />
      <div className="flex flex-wrap items-center gap-2">
        <DdlDialectSelect {...props} />
        <DdlEditorActions {...props} />
      </div>
    </header>
  );
}

function EditorIdentity() {
  const { t } = useTranslation("sandbox-deployment");
  return (
    <div className="flex items-center gap-2 text-xs font-bold tracking-wide">
      <Code2 className="size-4 text-sky-400" aria-hidden="true" />
      <span className="text-slate-100">{t("TXT_EDITOR_TITLE")}</span>
      <Badge className="border-emerald-500/20 bg-emerald-500/10 text-emerald-400">
        {t("TXT_EDITABLE")}
      </Badge>
    </div>
  );
}

function DdlDialectSelect(props: DdlEditorToolbarProps) {
  const { t } = useTranslation("sandbox-deployment");
  const handleChange = (value: string) => {
    if (isDdlDialect(value)) props.onDialectChange(value);
  };
  return (
    <NativeSelect size="sm" value={props.dialect} disabled={props.isRefreshing}
      aria-label={t("DDL_DIALECT_LABEL")} selectClassName="border-slate-700 bg-slate-800 text-slate-200"
      onChange={(event) => handleChange(event.target.value)}>
      {SUPPORTED_DDL_DIALECTS.map((dialect) => (
        <NativeSelectOption key={dialect} value={dialect}>
          {t(`TXT_DIALECT_${dialect}`)}
        </NativeSelectOption>
      ))}
    </NativeSelect>
  );
}

function DdlEditorActions(props: DdlEditorToolbarProps) {
  const { t } = useTranslation("sandbox-deployment");
  return (
    <>
      <ToolbarButton icon={props.isRefreshing ? <Loader2 className="animate-spin" /> : <Wand2 />} onClick={props.onFormatDdl}>{t("BTN_FORMAT_SQL")}</ToolbarButton>
      <ToolbarButton icon={<Copy />} onClick={props.onCopyDdl}>{t("BTN_COPY_DDL")}</ToolbarButton>
      <ToolbarButton icon={<FileText />} onClick={props.onDownloadDocument}>{t("BTN_DOWNLOAD_DOC")}</ToolbarButton>
      <ToolbarButton icon={<Download />} onClick={props.onDownloadSql}>{t("BTN_DOWNLOAD_SQL")}</ToolbarButton>
    </>
  );
}

function ToolbarButton(props: {
  children: ReactNode;
  icon: ReactNode;
  onClick: () => void;
}) {
  return (
    <Button type="button" size="sm" variant="secondary" onClick={props.onClick}>
      <span className="[&>svg]:size-3.5" aria-hidden="true">{props.icon}</span>
      {props.children}
    </Button>
  );
}
