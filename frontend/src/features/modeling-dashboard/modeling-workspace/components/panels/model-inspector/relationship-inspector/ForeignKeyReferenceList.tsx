"use client";

import { Trash2 } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import type { DbmlReference } from "../../../../model-document/dbml/types";

interface ForeignKeyReferenceListProps {
  references: DbmlReference[];
  onRemove: (referenceId: string) => void;
}

export function ForeignKeyReferenceList(props: ForeignKeyReferenceListProps) {
  const { t } = useTranslation("model-inspector");
  return props.references.map((reference) => (
    <div
      key={reference.id}
      className="flex items-center justify-between gap-2 rounded bg-muted/50 p-2 text-xs"
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
        aria-label={t("BTN_DELETE_FOREIGN_KEY")}
        onClick={() => props.onRemove(reference.id)}
      >
        <Trash2 />
      </Button>
    </div>
  ));
}
