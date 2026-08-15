"use client";

import type { CSSProperties } from "react";
import { useTranslation } from "react-i18next";
import type { DbmlDocument } from "@/common/dbml/types";
import type { DataModelAction } from "../../model-document/reducers/data-model-editor-reducer";
import type { DataModelValidationErrors } from "../../model-document/types/data-model-validation-types";
import {
  MAX_INSPECTOR_WIDTH_PX,
  MIN_INSPECTOR_WIDTH_PX,
  useResizableInspector,
} from "../hooks/use-resizable-inspector";
import { InspectorHeader } from "./shared/InspectorHeader";
import { RelationshipInspector } from "./relationship-inspector/RelationshipInspector";
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

/** Hiển thị inspector theo table hoặc relationship đang chọn.
 * @param props Document, selection và reducer command.
 * @returns Dock inspector responsive bên phải workspace.
 */
export function DataModelInspector(props: DataModelInspectorProps) {
  const { t } = useTranslation("modeling-dashboard");
  const resize = useResizableInspector();
  const table = props.document.tables.find(
    (item) => item.id === props.selectedTableId,
  );
  const reference = props.document.references.find(
    (item) => item.id === props.selectedReferenceId,
  );
  const tableIndex = table ? props.document.tables.indexOf(table) : -1;
  const referenceIndex = reference
    ? props.document.references.indexOf(reference)
    : -1;
  const handleDeleteTable = () => {
    if (!table) return;
    props.mutate({ type: "remove-table", tableId: table.id });
    props.onClearSelection();
  };
  return (
    <aside
      style={{ "--inspector-width": `${resize.width}px` } as CSSProperties}
      className="pointer-events-auto fixed inset-x-0 bottom-0 z-30 max-h-[55vh] min-h-0 min-w-0 shrink-0 overflow-hidden border bg-white shadow-xl lg:relative lg:inset-auto lg:h-full lg:max-h-full lg:w-(--inspector-width) lg:flex-none lg:border-y-0 lg:border-r-0 lg:shadow-none"
    >
      <div
        role="separator"
        aria-label={t("BTN_RESIZE_INSPECTOR")}
        aria-orientation="vertical"
        aria-valuemin={MIN_INSPECTOR_WIDTH_PX}
        aria-valuemax={MAX_INSPECTOR_WIDTH_PX}
        aria-valuenow={resize.width}
        tabIndex={0}
        onPointerDown={resize.handlePointerDown}
        onPointerMove={resize.handlePointerMove}
        onPointerUp={resize.handlePointerUp}
        onPointerCancel={resize.handlePointerCancel}
        onLostPointerCapture={resize.handlePointerCancel}
        onKeyDown={resize.handleKeyDown}
        className="absolute inset-y-0 left-0 z-40 hidden w-2 cursor-col-resize touch-none bg-transparent outline-none transition-colors hover:bg-blue-400 focus-visible:bg-blue-400 lg:block"
      />
      <div className="max-h-[55vh] touch-pan-x touch-pan-y overflow-auto overscroll-contain lg:h-full lg:max-h-full">
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
            tableIndex={tableIndex}
            validationErrors={props.validationErrors}
            mutate={props.mutate}
            onAddColumn={props.onAddColumn}
          />
        )}
        {reference && (
          <RelationshipInspector
            document={props.document}
            reference={reference}
            referenceIndex={referenceIndex}
            validationErrors={props.validationErrors}
            mutate={props.mutate}
            onDeleted={props.onClearSelection}
          />
        )}
        {!table && !reference && (
          <p className="p-5 text-sm leading-6 text-slate-500">
            {t("TXT_INSPECTOR_EMPTY")}
          </p>
        )}
      </div>
    </aside>
  );
}
