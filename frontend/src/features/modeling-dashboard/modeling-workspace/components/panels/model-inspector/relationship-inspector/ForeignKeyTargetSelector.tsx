"use client";

import { Plus } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import {
  NativeSelect,
  NativeSelectOption,
} from "@/common/components/ui/native-select";
import type {
  DbmlColumn,
  DbmlTable,
} from "../../../../model-document/dbml/types";

interface ForeignKeyTargetSelectorProps {
  tables: DbmlTable[];
  targetTable: DbmlTable | undefined;
  columns: DbmlColumn[];
  selectedColumn: DbmlColumn | undefined;
  alreadyExists: boolean;
  onChangeTable: (tableName: string) => void;
  onChangeColumn: (columnName: string) => void;
  onAdd: () => void;
}

export function ForeignKeyTargetSelector(props: ForeignKeyTargetSelectorProps) {
  const { t } = useTranslation("model-inspector");
  return (
    <div className="grid gap-2 sm:grid-cols-[1fr_1fr_auto]">
      <NativeSelect
        className="w-full"
        aria-label={t("TO_TABLE_LABEL")}
        value={props.targetTable?.name ?? ""}
        onChange={(event) => props.onChangeTable(event.target.value)}
      >
        {props.tables.map((table) => (
          <NativeSelectOption key={table.id} value={table.name}>
            {table.name}
          </NativeSelectOption>
        ))}
      </NativeSelect>
      <NativeSelect
        className="w-full"
        aria-label={t("TO_COLUMNS_LABEL")}
        value={props.selectedColumn?.name ?? ""}
        onChange={(event) => props.onChangeColumn(event.target.value)}
      >
        {props.columns.map((column) => (
          <NativeSelectOption key={column.id} value={column.name}>
            {column.name}
          </NativeSelectOption>
        ))}
      </NativeSelect>
      <Button
        type="button"
        size="sm"
        variant="outline"
        disabled={!props.selectedColumn || props.alreadyExists}
        onClick={props.onAdd}
      >
        <Plus />
        {t("BTN_ADD_FOREIGN_KEY")}
      </Button>
    </div>
  );
}
