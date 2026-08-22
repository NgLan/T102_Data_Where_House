"use client";

import { LocateFixed, Network, Search } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import { Input } from "@/common/components/ui/input";

interface ERDCanvasToolbarProps {
  query: string;
  onChangeQuery: (query: string) => void;
  onFindTable: () => void;
  onAutoLayout: () => void;
}

export function ERDCanvasToolbar(props: ERDCanvasToolbarProps) {
  const { t } = useTranslation("modeling-workspace");
  return (
    <div className="flex items-center gap-2 border-b bg-card px-3 py-2">
      <Network className="size-4 shrink-0 text-primary" aria-hidden="true" />
      <strong className="shrink-0 whitespace-nowrap text-xs text-foreground">
        {t("TXT_CANVAS_TITLE")}
      </strong>
      <div className="flex min-w-0 flex-1 items-center gap-1">
        <Input
          value={props.query}
          onChange={(event) => props.onChangeQuery(event.target.value)}
          onKeyDown={(event) =>
            event.key === "Enter" && props.onFindTable()
          }
          placeholder={t("TABLE_SEARCH_PLACEHOLDER")}
          className="h-7 min-w-0 flex-1"
        />
        <Button
          type="button"
          size="icon-sm"
          variant="outline"
          onClick={props.onFindTable}
          aria-label={t("BTN_FIND_TABLE")}
        >
          <Search />
        </Button>
      </div>
      <Button
        type="button"
        size="sm"
        variant="outline"
        onClick={props.onAutoLayout}
        className="shrink-0 whitespace-nowrap"
      >
        <LocateFixed />
        {t("BTN_AUTO_LAYOUT")}
      </Button>
    </div>
  );
}
