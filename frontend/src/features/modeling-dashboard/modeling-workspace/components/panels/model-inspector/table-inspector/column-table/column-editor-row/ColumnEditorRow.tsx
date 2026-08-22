"use client";

import { useState } from "react";
import { useTranslation } from "react-i18next";
import { ConfirmationDialog } from "@/common/components/ui/ConfirmationDialog";
import { isValidDbmlDataType } from "@/features/modeling-dashboard/modeling-workspace/model-document/dbml/data-type";
import type {
  DbmlColumn,
  DbmlDocument,
  DbmlTable,
} from "@/features/modeling-dashboard/modeling-workspace/model-document/dbml/types";
import type { DataModelAction } from "../../../../../../model-document/reducers/data-model-editor-reducer";
import type { DataModelValidationErrors } from "../../../../../../model-document/types/data-model-validation-types";
import {
  getDataTypeChangeImpact,
  hasDataTypeImpact,
} from "../../../../../../model-document/utils/column-constraints";
import { getColumnReferences } from "../../../../../../model-document/utils/column-reference-impact";
import { ColumnSettings } from "./column-settings/ColumnSettings";
import { ColumnEditorSummary } from "./ColumnEditorSummary";

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
  const { t } = useTranslation(["model-inspector", "common"]);
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
    else updateDataType(props, value);
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
  const isFK =
    getColumnReferences(props.document, props.table, props.column).length > 0;
  return (
    <section>
      <ColumnEditorSummary
        column={props.column}
        tableId={props.table.id}
        nameError={props.validationErrors[`${path}.name`]}
        dataTypeError={props.validationErrors[`${path}.dataType`]}
        isForeignKey={isFK}
        isExpanded={isExpanded}
        mutate={props.mutate}
        onChangeDataType={handleChangeDataType}
        onToggleExpanded={() => setIsExpanded((current) => !current)}
      />
      {isExpanded && <ColumnSettings {...props} path={path} />}
      <ConfirmationDialog
        isOpen={pendingDataType !== null}
        onOpenChange={(isOpen) => !isOpen && setPendingDataType(null)}
        title={t("model-inspector:TXT_DATA_TYPE_IMPACT_TITLE")}
        content={t("model-inspector:TXT_DATA_TYPE_IMPACT_DESCRIPTION")}
        actions={[
          { id: "cancel", label: t("common:BTN_CANCEL"), variant: "outline" },
          {
            id: "confirm",
            label: t("model-inspector:BTN_CHANGE_AND_CLEAN"),
            variant: "destructive",
            onSelect: handleConfirmDataType,
          },
        ]}
      />
    </section>
  );
}

function updateDataType(props: ColumnEditorRowProps, value: string): void {
  props.mutate({
    type: "update-column",
    tableId: props.table.id,
    columnId: props.column.id,
    field: "dataType",
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
