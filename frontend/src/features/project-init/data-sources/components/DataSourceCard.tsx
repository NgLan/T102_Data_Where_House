"use client";

import { Database, Trash2 } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { DataSourceResponse, UpdateDataSourceColumnRequest } from "@/api";
import { Button } from "@/common/components/ui/button";
import { ConfirmationDialog } from "@/common/components/ui/confirmation-dialog";
import { DataPreview } from "./DataPreview";
import { SchemaTable } from "./SchemaTable";

interface DataSourceCardProps {
  projectId: string;
  source: DataSourceResponse;
  canEdit: boolean;
  disabled: boolean;
  onDelete: (sourceId: string) => void;
  onUpdate: (sourceId: string, body: UpdateDataSourceColumnRequest) => void;
}

/** Một source thật gồm schema chỉnh được, preview read-only và delete có xác nhận.
 * @param props Data Source, quyền chỉnh sửa và callback cập nhật/xóa.
 * @returns Card quản lý một Data Source.
 */
export function DataSourceCard(props: DataSourceCardProps) {
  const { t } = useTranslation("project-init");
  return <article className="space-y-4 rounded-xl border bg-background p-4">
    <header className="flex flex-wrap items-start justify-between gap-3">
      <div className="flex min-w-0 items-center gap-3">
        <span className="rounded-lg bg-muted p-2"><Database className="size-4" /></span>
        <div className="min-w-0">
          <h3 className="truncate font-medium">{props.source.name}</h3>
          <p className="text-xs text-muted-foreground">{props.source.type}</p>
        </div>
      </div>
      {props.canEdit && <ConfirmationDialog
        trigger={<Button type="button" size="sm" variant="destructive" disabled={props.disabled}>
          <Trash2 />{t("BTN_DELETE_SOURCE")}
        </Button>}
        title={t("TXT_DELETE_CONFIRM_TITLE")}
        content={t("TXT_DELETE_CONFIRM_DESCRIPTION", { name: props.source.name })}
        actions={[
          { id: "cancel", label: t("BTN_CANCEL"), variant: "outline" },
          { id: "delete", label: t("BTN_CONFIRM_DELETE"), variant: "destructive",
            isDisabled: props.disabled, onSelect: () => props.onDelete(props.source.id) },
        ]} />}
    </header>
    <div className="space-y-3">{(props.source.tables ?? []).map((table) =>
      <SchemaTable key={table.name} sourceId={props.source.id} table={table}
        canEdit={props.canEdit} disabled={props.disabled} onUpdate={props.onUpdate} />)}
    </div>
    <DataPreview projectId={props.projectId} sourceId={props.source.id} />
  </article>;
}
