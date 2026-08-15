"use client";

import { Link2, Plus, Table2 } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import type {
  DbmlDocument,
  DbmlReference,
  DbmlTable,
} from "@/common/dbml/types";
import { ModelDeleteConfirmationDialog } from "./ModelDeleteConfirmationDialog";

interface InspectorHeaderProps {
  document: DbmlDocument;
  table?: DbmlTable;
  reference?: DbmlReference;
  onAddTable: () => void;
  onDeleteTable: () => void;
}

/** Hiển thị title theo selection và nhóm thao tác table ở cùng một vị trí. */
export function InspectorHeader(props: InspectorHeaderProps) {
  const { t } = useTranslation("modeling-dashboard");
  const relationshipCount = props.table
    ? props.document.references.filter(
        (item) =>
          item.fromTable === props.table?.name ||
          item.toTable === props.table?.name,
      ).length
    : 0;
  return (
    <header className="sticky top-0 z-10 flex items-center justify-between border-b bg-white px-4 py-3">
      <strong className="flex items-center gap-2 text-sm text-slate-800">
        {props.reference ? (
          <Link2 className="size-4" />
        ) : (
          <Table2 className="size-4" />
        )}
        {props.reference
          ? t("TXT_RELATIONSHIP_DETAIL")
          : t("TXT_TABLE_DETAIL", { name: props.table?.name ?? "" })}
      </strong>
      <div className="flex items-center gap-2">
        <Button
          type="button"
          size="sm"
          variant="outline"
          className="cursor-pointer"
          onClick={props.onAddTable}
        >
          <Plus />
          {t("BTN_ADD_TABLE")}
        </Button>
        {props.table && (
          <ModelDeleteConfirmationDialog
            title={t("TXT_DELETE_TABLE", { name: props.table.name })}
            description={t("TXT_DELETE_DEPENDENCY", {
              count: relationshipCount,
            })}
            onConfirm={props.onDeleteTable}
          />
        )}
      </div>
    </header>
  );
}
