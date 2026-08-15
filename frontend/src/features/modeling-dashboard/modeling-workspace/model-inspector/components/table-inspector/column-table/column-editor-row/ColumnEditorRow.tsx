"use client";

import { ChevronDown, ChevronRight, KeyRound } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import { ConfirmationDialog } from "@/common/components/ui/confirmation-dialog";
import { Input } from "@/common/components/ui/input";
import { isValidDbmlDataType } from "@/common/dbml/data-type";
import type { DbmlColumn, DbmlDocument, DbmlTable } from "@/common/dbml/types";
import type { DataModelAction } from "../../../../../model-document/reducers/data-model-editor-reducer";
import type { DataModelValidationErrors } from "../../../../../model-document/types/data-model-validation-types";
import {
  getColumnReferences,
  getDataTypeChangeImpact,
  hasDataTypeImpact,
} from "../../../../../model-document/utils/column-constraints";
import { ColumnSettings } from "./column-settings/ColumnSettings";
import { DataTypeField } from "./data-type-field/DataTypeField";
import { ModelDeleteConfirmationDialog } from "../../../shared/ModelDeleteConfirmationDialog";
import { ValidationMessage } from "../../../shared/ValidationMessage";

interface ColumnEditorRowProps {
  document: DbmlDocument;
  table: DbmlTable;
  tableIndex: number;
  column: DbmlColumn;
  columnIndex: number;
  validationErrors: DataModelValidationErrors;
  mutate: (action: DataModelAction) => void;
}

/** Điều phối dòng tóm tắt, detail và xác nhận ảnh hưởng khi đổi data type. */
export function ColumnEditorRow(props: ColumnEditorRowProps) {
  const { t } = useTranslation(["modeling-dashboard", "common"]);
  const [isExpanded, setIsExpanded] = useState(false);
  const [pendingDataType, setPendingDataType] = useState<string | null>(null);
  const path = `tables.${props.tableIndex}.columns.${props.columnIndex}`;
  const handleChangeDataType = (value: string) => {
    const impact = getDataTypeChangeImpact({
      document: props.document,
      table: props.table,
      column: props.column,
      nextDataType: value,
    });
    if (isValidDbmlDataType(value) && hasDataTypeImpact(impact))
      setPendingDataType(value);
    else updateColumn(props, "dataType", value);
  };
  const handleConfirmDataType = () => {
    if (pendingDataType === null) return;
    const impact = getDataTypeChangeImpact({
      document: props.document,
      table: props.table,
      column: props.column,
      nextDataType: pendingDataType,
    });
    props.mutate({
      type: "update-column-settings",
      tableId: props.table.id,
      columnId: props.column.id,
      patch: createTypePatch(pendingDataType, impact),
      removeReferenceIds: impact.referenceIds,
    });
    setPendingDataType(null);
  };
  const isPK = props.column.isPrimaryKey;
  const isFK =
    getColumnReferences(props.document, props.table, props.column).length > 0;
  return (
    <section>
      <div className="grid gap-2 p-3 md:grid-cols-[1fr_1.2fr_auto_auto] md:items-start">
        <FieldWithError code={props.validationErrors[`${path}.name`]}>
          <div className="relative flex items-center">
            {(isPK || isFK) && (
              <div className="absolute left-2.5 z-10 flex pointer-events-none items-center gap-1">
                {isPK ? (
                  <KeyRound
                    className="size-3.5 text-amber-500 shrink-0"
                    aria-label="Primary Key"
                  />
                ) : isFK ? (
                  <KeyRound
                    className="size-3.5 text-blue-500 shrink-0"
                    aria-label="Foreign Key"
                  />
                ) : null}
              </div>
            )}
            <Input
              aria-label={t("modeling-dashboard:COLUMN_NAME_LABEL")}
              value={props.column.name}
              className={isPK || isFK ? "pl-7" : ""}
              onChange={(event) =>
                updateColumn(props, "name", event.target.value)
              }
            />
          </div>
        </FieldWithError>
        <FieldWithError code={props.validationErrors[`${path}.dataType`]}>
          <DataTypeField
            value={props.column.dataType}
            isInvalid={Boolean(props.validationErrors[`${path}.dataType`])}
            onChange={handleChangeDataType}
          />
        </FieldWithError>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className="cursor-pointer"
          aria-expanded={isExpanded}
          onClick={() => setIsExpanded((current) => !current)}
        >
          {isExpanded ? <ChevronDown /> : <ChevronRight />}
          {t("modeling-dashboard:BTN_COLUMN_SETTINGS")}
        </Button>
        <ModelDeleteConfirmationDialog
          title={t("modeling-dashboard:TXT_DELETE_COLUMN", {
            name: props.column.name,
          })}
          description={t("modeling-dashboard:TXT_DELETE_COLUMN_DESCRIPTION")}
          onConfirm={() =>
            props.mutate({
              type: "remove-column",
              tableId: props.table.id,
              columnId: props.column.id,
            })
          }
        />
      </div>
      {isExpanded && <ColumnSettings {...props} path={path} />}
      <ConfirmationDialog
        isOpen={pendingDataType !== null}
        onOpenChange={(isOpen) => !isOpen && setPendingDataType(null)}
        title={t("modeling-dashboard:TXT_DATA_TYPE_IMPACT_TITLE")}
        content={t("modeling-dashboard:TXT_DATA_TYPE_IMPACT_DESCRIPTION")}
        actions={[
          { id: "cancel", label: t("common:BTN_CANCEL"), variant: "outline" },
          {
            id: "confirm",
            label: t("modeling-dashboard:BTN_CHANGE_AND_CLEAN"),
            variant: "destructive",
            onSelect: handleConfirmDataType,
          },
        ]}
      />
    </section>
  );
}

function updateColumn(
  props: ColumnEditorRowProps,
  field: keyof DbmlColumn,
  value: string | boolean,
) {
  props.mutate({
    type: "update-column",
    tableId: props.table.id,
    columnId: props.column.id,
    field,
    value,
  });
}

function createTypePatch(
  value: string,
  impact: ReturnType<typeof getDataTypeChangeImpact>,
): Partial<DbmlColumn> {
  return {
    dataType: value,
    ...(impact.shouldClearDefault ? { defaultValue: "" } : {}),
    ...(impact.shouldDisableIncrement ? { isAutoIncrement: false } : {}),
  };
}

function FieldWithError({
  code,
  children,
}: {
  code?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-1">
      {children}
      <ValidationMessage code={code} />
    </div>
  );
}
