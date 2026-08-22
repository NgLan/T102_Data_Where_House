"use client";

import { useTranslation } from "react-i18next";
import type { DbmlDocument } from "../../../model-document/dbml/types";
import type { DataModelAction } from "../../../model-document/reducers/data-model-editor-reducer";
import type { DataModelValidationErrors } from "../../../model-document/types/data-model-validation-types";
import { RelationshipInspector } from "./relationship-inspector/RelationshipInspector";
import { InspectorHeader } from "./shared/InspectorHeader";
import { TableInspector } from "./table-inspector/TableInspector";

interface DataModelInspectorProps {
  document: DbmlDocument;
  selectedTableId: string | null;
  selectedReferenceId: string | null;
  validationErrors: DataModelValidationErrors;
  mutate: (action: DataModelAction) => void;
  onAddTable: () => void;
  onAddColumn: (tableId: string) => void;
  onClearSelection: () => void;
}

/** Hiển thị chi tiết bảng hoặc relationship trong panel do workspace quản lý. */
export function DataModelInspector(props: DataModelInspectorProps) {
  const { t } = useTranslation("model-inspector");
  const table = props.document.tables.find(
    (item) => item.id === props.selectedTableId,
  );
  const reference = props.document.references.find(
    (item) => item.id === props.selectedReferenceId,
  );
  const handleDeleteTable = () => {
    if (!table) return;
    props.mutate({ type: "remove-table", tableId: table.id });
    props.onClearSelection();
  };
  return (
    <aside className="h-full min-h-0 overflow-auto border-l bg-card">
      <InspectorHeader
        document={props.document}
        table={table}
        reference={reference}
        onAddTable={props.onAddTable}
        onDeleteTable={handleDeleteTable}
      />
      {table && (
        <TableInspector
          document={props.document}
          table={table}
          tableIndex={props.document.tables.indexOf(table)}
          validationErrors={props.validationErrors}
          mutate={props.mutate}
          onAddColumn={props.onAddColumn}
        />
      )}
      {reference && (
        <RelationshipInspector
          document={props.document}
          reference={reference}
          referenceIndex={props.document.references.indexOf(reference)}
          validationErrors={props.validationErrors}
          mutate={props.mutate}
          onDeleted={props.onClearSelection}
        />
      )}
      {!table && !reference && (
        <p className="p-5 text-sm leading-6 text-muted-foreground">
          {t("TXT_INSPECTOR_EMPTY")}
        </p>
      )}
    </aside>
  );
}
