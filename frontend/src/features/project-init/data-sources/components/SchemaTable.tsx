"use client";

import { useState } from "react";
import { Settings2 } from "lucide-react";
import { useTranslation } from "react-i18next";
import type {
  DataSourceColumnResponse,
  DataSourceTableResponse,
  UpdateDataSourceColumnRequest,
} from "@/api";
import { Button } from "@/common/components/ui/button";
import {
  NativeSelect,
  NativeSelectOption,
} from "@/common/components/ui/native-select";
import { ColumnOptionsDialog } from "./ColumnOptionsDialog";

const COLUMN_TYPES = [
  "TEXT",
  "NUMBER",
  "DATETIME",
  "BOOLEAN",
  "OPTION",
] as const;

interface SchemaTableProps {
  sourceId: string;
  table: DataSourceTableResponse;
  canEdit: boolean;
  disabled: boolean;
  onUpdate: (sourceId: string, body: UpdateDataSourceColumnRequest) => void;
}

/** Hiển thị schema và gửi từng thay đổi cột qua PATCH chuyên biệt.
 * @param props Schema, quyền chỉnh sửa và callback cập nhật metadata cột.
 * @returns Bảng schema của Data Source.
 */
export function SchemaTable(props: SchemaTableProps) {
  const { t } = useTranslation("project-init");
  const [editing, setEditing] = useState<DataSourceColumnResponse | null>(null);
  const update = (
    column: DataSourceColumnResponse,
    dataType: string,
    options: string[] = [],
  ) => {
    props.onUpdate(props.sourceId, {
      table_name: props.table.name,
      column_name: column.name,
      data_type: dataType as UpdateDataSourceColumnRequest["data_type"],
      options,
    });
  };
  return (
    <div className="overflow-hidden rounded-lg border">
      <div className="border-b bg-muted/50 px-3 py-2 text-sm font-medium">
        {props.table.name}
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="text-xs text-muted-foreground">
            <tr>
              <th className="px-3 py-2">{t("LBL_COLUMN_NAME")}</th>
              <th className="px-3 py-2">{t("LBL_COLUMN_TYPE")}</th>
              <th className="px-3 py-2">{t("LBL_COLUMN_RULES")}</th>
            </tr>
          </thead>
          <tbody>
            {(props.table.columns ?? []).map((column) => (
              <tr key={column.name} className="border-t">
                <td className="px-3 py-2 font-mono text-xs">{column.name}</td>
                <td className="px-3 py-2">
                  <div className="flex items-center gap-2">
                    <NativeSelect
                      value={column.data_type}
                      disabled={!props.canEdit || props.disabled}
                      onChange={(event) =>
                        event.target.value === "OPTION"
                          ? setEditing(column)
                          : update(column, event.target.value)
                      }
                    >
                      {COLUMN_TYPES.map((type) => (
                        <NativeSelectOption key={type} value={type}>
                          {type}
                        </NativeSelectOption>
                      ))}
                    </NativeSelect>
                    {column.data_type === "OPTION" && props.canEdit && (
                      <Button
                        type="button"
                        size="icon-sm"
                        variant="ghost"
                        aria-label={t("BTN_EDIT_OPTIONS")}
                        onClick={() => setEditing(column)}
                      >
                        <Settings2 />
                      </Button>
                    )}
                  </div>
                </td>
                <td className="px-3 py-2 text-xs text-muted-foreground">
                  {[
                    column.primary_key && t("TXT_PRIMARY_KEY"),
                    column.nullable && t("TXT_NULLABLE"),
                  ]
                    .filter(Boolean)
                    .join(" · ") || "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {editing && (
        <ColumnOptionsDialog
          columnName={editing.name}
          options={editing.options ?? []}
          disabled={props.disabled}
          onClose={() => setEditing(null)}
          onSave={(options) => {
            if (editing) update(editing, "OPTION", options);
            setEditing(null);
          }}
        />
      )}
    </div>
  );
}
