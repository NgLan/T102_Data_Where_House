"use client";

import { Link2, Plus, Trash2 } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import {
  NativeSelect,
  NativeSelectOption,
} from "@/common/components/ui/native-select";
import { canonicalDbmlDataType } from "@/common/dbml/data-type";
import type { DbmlColumn, DbmlDocument, DbmlTable } from "@/common/dbml/types";
import type { DataModelAction } from "../../../model-document/reducers/data-model-editor-reducer";
import {
  getColumnReferences,
  getEffectiveColumnConstraints,
} from "../../../model-document/utils/column-constraints";

interface ForeignKeyFieldProps {
  document: DbmlDocument;
  table: DbmlTable;
  column: DbmlColumn;
  mutate: (action: DataModelAction) => void;
}

/** Quản lý foreign key đơn của cột bằng endpoint tồn tại trong document. */
export function ForeignKeyField(props: ForeignKeyFieldProps) {
  const { t } = useTranslation("modeling-dashboard");
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
    <fieldset className="space-y-3 rounded-lg border bg-white p-3">
      <legend className="flex items-center gap-1 text-xs font-medium text-slate-600">
        <Link2 />
        {t("FOREIGN_KEY_LABEL")}
      </legend>
      <div className="grid gap-2 sm:grid-cols-[1fr_1fr_auto]">
        <NativeSelect
          className="w-full"
          aria-label={t("TO_TABLE_LABEL")}
          value={targetTable?.name ?? ""}
          onChange={(event) => {
            setTargetTableName(event.target.value);
            setTargetColumnName("");
          }}
        >
          {props.document.tables.map((table) => (
            <NativeSelectOption key={table.id} value={table.name}>
              {table.name}
            </NativeSelectOption>
          ))}
        </NativeSelect>
        <NativeSelect
          className="w-full"
          aria-label={t("TO_COLUMNS_LABEL")}
          value={selectedColumn?.name ?? ""}
          onChange={(event) => setTargetColumnName(event.target.value)}
        >
          {candidates.map((column) => (
            <NativeSelectOption key={column.id} value={column.name}>
              {column.name}
            </NativeSelectOption>
          ))}
        </NativeSelect>
        <Button
          type="button"
          size="sm"
          variant="outline"
          className="cursor-pointer"
          disabled={!selectedColumn || alreadyExists}
          onClick={handleAddReference}
        >
          <Plus />
          {t("BTN_ADD_FOREIGN_KEY")}
        </Button>
      </div>
      {references.map((reference) => (
        <div
          key={reference.id}
          className="flex items-center justify-between gap-2 rounded bg-slate-50 p-2 text-xs"
        >
          <span>
            {reference.fromTable}.{reference.fromColumns.join(", ")}{" "}
            {reference.relation} {reference.toTable}.
            {reference.toColumns.join(", ")}
          </span>
          <Button
            type="button"
            size="icon-xs"
            variant="ghost"
            className="cursor-pointer"
            aria-label={t("BTN_DELETE_FOREIGN_KEY")}
            onClick={() =>
              props.mutate({
                type: "remove-reference",
                referenceId: reference.id,
              })
            }
          >
            <Trash2 />
          </Button>
        </div>
      ))}
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
