"use client";

import { useState } from "react";
import { ChevronDown, Database, Trash2 } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { DataSourceResponse } from "@/api";
import { Button } from "@/common/components/ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/common/components/ui/collapsible";
import { ConfirmationDialog } from "@/common/components/ui/ConfirmationDialog";
import { Empty, EmptyDescription, EmptyHeader, EmptyTitle } from "@/common/components/ui/empty";
import { DataSourcePreview } from "./DataSourcePreview";
import { DataSourceSchemaTable } from "./DataSourceSchemaTable";

interface DataSourceCardProps {
  projectId: string;
  source: DataSourceResponse;
  canEdit: boolean;
  disabled: boolean;
  onDelete: (sourceId: string) => void;
}

/** Card CSV đóng mặc định; delete độc lập với trigger mở card. */
export function DataSourceCard(props: DataSourceCardProps) {
  const { t } = useTranslation("project-init");
  const { t: tCommon } = useTranslation("common");
  const [isOpen, setIsOpen] = useState(false);
  return <Collapsible open={isOpen} onOpenChange={setIsOpen} asChild>
    <article className="rounded-xl border bg-background">
      <header className="flex items-center gap-2 p-3">
        <CollapsibleTrigger asChild><Button type="button" variant="ghost"
          className="min-w-0 flex-1 cursor-pointer justify-start px-2">
          <Database className="size-4 shrink-0" /><span className="truncate">{props.source.name}</span>
          <ChevronDown className={`ml-auto size-4 transition-transform ${isOpen ? "rotate-180" : ""}`} />
        </Button></CollapsibleTrigger>
        {props.canEdit && <ConfirmationDialog trigger={<Button type="button" size="icon-sm"
          variant="ghost" disabled={props.disabled} aria-label={tCommon("BTN_DELETE")}><Trash2 /></Button>}
          title={t("TXT_DELETE_CONFIRM_TITLE")}
          content={t("TXT_DELETE_CONFIRM_DESCRIPTION", { name: props.source.name })}
          actions={[
            { id: "cancel", label: tCommon("BTN_CANCEL"), variant: "outline" },
            { id: "delete", label: tCommon("BTN_DELETE"), variant: "destructive",
              isDisabled: props.disabled, onSelect: () => props.onDelete(props.source.id) },
          ]} />}
      </header>
      <CollapsibleContent className="space-y-4 border-t p-4">
        {props.source.analysis_status === "PENDING" ? <Empty><EmptyHeader>
          <EmptyTitle>{t("TXT_SOURCE_PENDING_TITLE")}</EmptyTitle>
          <EmptyDescription>{t("TXT_SOURCE_PENDING_DESCRIPTION")}</EmptyDescription>
        </EmptyHeader></Empty> : <>{props.source.tables.map((table) =>
          <DataSourceSchemaTable key={table.name} table={table} />)}
          <DataSourcePreview projectId={props.projectId} sourceId={props.source.id} /></>}
      </CollapsibleContent>
    </article>
  </Collapsible>;
}
