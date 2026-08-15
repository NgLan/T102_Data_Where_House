"use client";

import { Columns3 } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { DbmlDocument, DbmlTable } from "@/common/dbml/types";
import type { DataModelAction } from "../../../../model-document/reducers/data-model-editor-reducer";
import type { DataModelValidationErrors } from "../../../../model-document/types/data-model-validation-types";
import { ColumnEditorRow } from "./column-editor-row/ColumnEditorRow";

interface ColumnTableProps {
  document: DbmlDocument;
  table: DbmlTable;
  tableIndex: number;
  validationErrors: DataModelValidationErrors;
  mutate: (action: DataModelAction) => void;
}

/** Hiển thị danh sách cột gọn và mở rộng setting theo từng dòng. */
export function ColumnTable(props: ColumnTableProps) {
  const { t } = useTranslation("modeling-dashboard");
  if (!props.table.columns.length)
    return (
      <div className="rounded-lg border p-6 text-center text-sm text-slate-500">
        <Columns3 className="mx-auto mb-2 size-7 text-slate-300" />
        {t("TXT_EMPTY_COLUMNS")}
      </div>
    );
  return (
    <div className="divide-y rounded-lg border">
      {props.table.columns.map((column, columnIndex) => (
        <ColumnEditorRow
          key={column.id}
          {...props}
          column={column}
          columnIndex={columnIndex}
        />
      ))}
    </div>
  );
}
