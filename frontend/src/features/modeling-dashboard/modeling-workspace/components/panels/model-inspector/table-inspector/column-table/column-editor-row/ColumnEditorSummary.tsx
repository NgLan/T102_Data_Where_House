"use client";

import { ChevronDown, ChevronRight, KeyRound } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import { Input } from "@/common/components/ui/input";
import type { DbmlColumn } from "../../../../../../model-document/dbml/types";
import type { DataModelAction } from "../../../../../../model-document/reducers/data-model-editor-reducer";
import { ModelDeleteConfirmationDialog } from "../../../shared/ModelDeleteConfirmationDialog";
import { ValidationMessage } from "../../../shared/ValidationMessage";
import { DataTypeField } from "./data-type-field/DataTypeField";

interface ColumnEditorSummaryProps {
  column: DbmlColumn;
  tableId: string;
  nameError?: string;
  dataTypeError?: string;
  isForeignKey: boolean;
  isExpanded: boolean;
  mutate: (action: DataModelAction) => void;
  onChangeDataType: (value: string) => void;
  onToggleExpanded: () => void;
}

export function ColumnEditorSummary(props: ColumnEditorSummaryProps) {
  const { t } = useTranslation("model-inspector");
  const hasKey = props.column.isPrimaryKey || props.isForeignKey;
  return (
    <div className="grid gap-2 p-3 md:grid-cols-[1fr_1.2fr_auto_auto] md:items-start">
      <FieldWithError code={props.nameError}>
        <div className="relative flex items-center">
          <Input
            aria-label={t("COLUMN_NAME_LABEL")}
            value={props.column.name}
            className={hasKey ? "pl-7" : ""}
            onChange={(event) =>
              updateColumn(props, "name", event.target.value)
            }
          />
          {hasKey && (
            <KeyRound
              className={
                props.column.isPrimaryKey
                  ? "pointer-events-none absolute left-2.5 size-3.5 text-warning"
                  : "pointer-events-none absolute left-2.5 size-3.5 text-primary"
              }
              aria-label={
                props.column.isPrimaryKey
                  ? t("PRIMARY_KEY_LABEL")
                  : t("FOREIGN_KEY_LABEL")
              }
            />
          )}
        </div>
      </FieldWithError>
      <FieldWithError code={props.dataTypeError}>
        <DataTypeField
          value={props.column.dataType}
          isInvalid={Boolean(props.dataTypeError)}
          onChange={props.onChangeDataType}
        />
      </FieldWithError>
      <Button
        type="button"
        variant="ghost"
        size="sm"
        aria-expanded={props.isExpanded}
        onClick={props.onToggleExpanded}
      >
        {props.isExpanded ? <ChevronDown /> : <ChevronRight />}
        {t("BTN_COLUMN_SETTINGS")}
      </Button>
      <ModelDeleteConfirmationDialog
        title={t("TXT_DELETE_COLUMN", { name: props.column.name })}
        description={t("TXT_DELETE_COLUMN_DESCRIPTION")}
        onConfirm={() =>
          props.mutate({
            type: "remove-column",
            tableId: props.tableId,
            columnId: props.column.id,
          })
        }
      />
    </div>
  );
}

function updateColumn(
  props: ColumnEditorSummaryProps,
  field: keyof DbmlColumn,
  value: string | boolean,
) {
  props.mutate({
    type: "update-column",
    tableId: props.tableId,
    columnId: props.column.id,
    field,
    value,
  });
}

function FieldWithError(props: { code?: string; children: React.ReactNode }) {
  return (
    <div className="space-y-2">
      {props.children}
      <ValidationMessage code={props.code} />
    </div>
  );
}
