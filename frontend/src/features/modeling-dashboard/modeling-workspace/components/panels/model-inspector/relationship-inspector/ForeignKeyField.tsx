"use client";

import { Link2 } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { canonicalDbmlDataType } from "@/features/modeling-dashboard/modeling-workspace/model-document/dbml/data-type";
import type {
  DbmlColumn,
  DbmlDocument,
  DbmlTable,
} from "@/features/modeling-dashboard/modeling-workspace/model-document/dbml/types";
import type { DataModelAction } from "../../../../model-document/reducers/data-model-editor-reducer";
import { getEffectiveColumnConstraints } from "../../../../model-document/utils/column-constraints";
import { getColumnReferences } from "../../../../model-document/utils/column-reference-impact";
import { ForeignKeyReferenceList } from "./ForeignKeyReferenceList";
import { ForeignKeyTargetSelector } from "./ForeignKeyTargetSelector";

interface ForeignKeyFieldProps {
  document: DbmlDocument;
  table: DbmlTable;
  column: DbmlColumn;
  mutate: (action: DataModelAction) => void;
}

/** Quản lý foreign key đơn của cột bằng endpoint tồn tại trong document. */
export function ForeignKeyField(props: ForeignKeyFieldProps) {
  const { t } = useTranslation("model-inspector");
  const [targetTableName, setTargetTableName] = useState(
    props.document.tables[0]?.name ?? "",
  );
  const [targetColumnName, setTargetColumnName] = useState("");
  const targetTable =
    props.document.tables.find((table) => table.name === targetTableName) ??
    props.document.tables[0];
  const candidates = targetTable
    ? candidateColumns(targetTable, props.column)
    : [];
  const selectedColumn =
    candidates.find((column) => column.name === targetColumnName) ??
    candidates[0];
  const references = getColumnReferences(
    props.document,
    props.table,
    props.column,
  );
  const alreadyExists = references.some(
    (reference) =>
      reference.fromTable === props.table.name &&
      reference.fromSchema === props.table.schemaName &&
      reference.fromColumns.includes(props.column.name) &&
      reference.toSchema === targetTable?.schemaName &&
      reference.toTable === targetTable?.name &&
      reference.toColumns.includes(selectedColumn?.name ?? ""),
  );
  const handleAddReference = () => {
    if (!targetTable || !selectedColumn) return;
    props.mutate({
      type: "add-reference",
      reference: {
        id: crypto.randomUUID(),
        fromSchema: props.table.schemaName,
        fromTable: props.table.name,
        fromColumn: props.column.name,
        fromColumns: [props.column.name],
        relation: ">",
        toSchema: targetTable.schemaName,
        toTable: targetTable.name,
        toColumn: selectedColumn.name,
        toColumns: [selectedColumn.name],
      },
    });
  };
  return (
    <fieldset className="space-y-3 rounded-lg border bg-card p-3">
      <legend className="flex items-center gap-1 text-xs font-medium text-muted-foreground">
        <Link2 />
        {t("FOREIGN_KEY_LABEL")}
      </legend>
      <ForeignKeyTargetSelector
        tables={props.document.tables}
        targetTable={targetTable}
        columns={candidates}
        selectedColumn={selectedColumn}
        alreadyExists={alreadyExists}
        onChangeTable={(tableName) => {
          setTargetTableName(tableName);
          setTargetColumnName("");
        }}
        onChangeColumn={setTargetColumnName}
        onAdd={handleAddReference}
      />
      <ForeignKeyReferenceList
        references={references}
        onRemove={(referenceId) =>
          props.mutate({ type: "remove-reference", referenceId })
        }
      />
    </fieldset>
  );
}

function candidateColumns(table: DbmlTable, source: DbmlColumn): DbmlColumn[] {
  return table.columns.filter((column) => {
    const constraints = getEffectiveColumnConstraints(table, column);
    return (
      constraints.isUnique &&
      canonicalDbmlDataType(column.dataType) ===
        canonicalDbmlDataType(source.dataType)
    );
  });
}
