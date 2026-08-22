"use client";

import { Plus } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import { Input } from "@/common/components/ui/input";
import { Textarea } from "@/common/components/ui/textarea";
import type {
  DbmlDocument,
  DbmlTable,
} from "@/features/modeling-dashboard/modeling-workspace/model-document/dbml/types";
import type { DataModelValidationErrors } from "../../../../model-document/types/data-model-validation-types";
import type { DataModelAction } from "../../../../model-document/reducers/data-model-editor-reducer";
import { ColumnTable } from "./column-table/ColumnTable";
import { ValidationMessage } from "../shared/ValidationMessage";

interface TableInspectorProps {
  document: DbmlDocument;
  table: DbmlTable;
  tableIndex: number;
  validationErrors: DataModelValidationErrors;
  mutate: (action: DataModelAction) => void;
  onAddColumn: (tableId: string) => void;
}

/** Chỉnh sửa table và column đang chọn trong dock inspector.
 * @param props Table hiện hành và các command của draft reducer.
 * @returns Form chỉnh sửa table/column không tạo state nghiệp vụ riêng.
 */
export function TableInspector(props: TableInspectorProps) {
  const { t } = useTranslation("model-inspector");
  const tableNameId = `table-name-${props.table.id}`;
  const tableNoteId = `table-note-${props.table.id}`;
  const updateTable = (field: "name" | "note", value: string) =>
    props.mutate({
      type: "update-table",
      tableId: props.table.id,
      field,
      value,
    });
  return (
    <div className="space-y-4 p-4">
      <div className="min-w-80 space-y-2">
        <label
          htmlFor={tableNameId}
          className="text-xs font-medium text-muted-foreground"
        >
          {t("TABLE_NAME_LABEL")}
        </label>
        <div className="min-w-0 flex-1">
          <Input
            id={tableNameId}
            aria-invalid={Boolean(
              props.validationErrors[`tables.${props.tableIndex}.name`],
            )}
            value={props.table.name}
            onChange={(event) => updateTable("name", event.target.value)}
          />
          <ValidationMessage
            code={props.validationErrors[`tables.${props.tableIndex}.name`]}
          />
        </div>
        <label
          htmlFor={tableNoteId}
          className="text-xs font-medium text-muted-foreground"
        >
          {t("TABLE_NOTE_LABEL")}
        </label>
        <Textarea
          id={tableNoteId}
          placeholder={t("TABLE_NOTE_PLACEHOLDER")}
          value={props.table.note}
          onChange={(event) => updateTable("note", event.target.value)}
        />
      </div>
      <div className="flex items-center justify-between border-t pt-3">
        <strong className="text-xs text-foreground">{t("TXT_COLUMNS")}</strong>
        <Button
          type="button"
          size="sm"
          variant="outline"
          onClick={() => props.onAddColumn(props.table.id)}
        >
          <Plus />
          {t("BTN_ADD_COLUMN")}
        </Button>
      </div>
      <ColumnTable
        document={props.document}
        table={props.table}
        tableIndex={props.tableIndex}
        validationErrors={props.validationErrors}
        mutate={props.mutate}
      />
    </div>
  );
}
