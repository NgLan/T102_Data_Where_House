"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import { Skeleton } from "@/common/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/common/components/ui/table";
import { projectInitQueryKeys } from "../../../constants/project-init-query-keys";
import { getDataSourcePreview } from "../services/data-sources-api";

/** Preview CSV đọc lười và được cache theo source. */
export function DataSourcePreview({
  projectId,
  sourceId,
}: {
  projectId: string;
  sourceId: string;
}) {
  const { t } = useTranslation("project-init");
  const { t: tCommon } = useTranslation("common");
  const [isOpen, setIsOpen] = useState(false);
  const query = useQuery({
    queryKey: projectInitQueryKeys.preview(projectId, sourceId),
    queryFn: () => getDataSourcePreview(projectId, sourceId),
    enabled: isOpen,
  });
  const rows = query.data?.rows ?? [];
  const columns = rows[0] ? Object.keys(rows[0]) : [];
  return (
    <div>
      <Button
        type="button"
        size="sm"
        variant="outline"
        onClick={() => setIsOpen(!isOpen)}
      >
        {t(isOpen ? "BTN_HIDE_PREVIEW" : "BTN_SHOW_PREVIEW")}
      </Button>
      {isOpen && (
        <div className="mt-3">
          {query.isLoading ? (
            <Skeleton className="h-32 w-full" />
          ) : query.isError ? (
            <div className="rounded-lg border border-destructive/30 p-4 text-sm">
              <p>{t("TXT_PREVIEW_ERROR")}</p>
              <Button
                className="mt-2"
                type="button"
                size="sm"
                variant="outline"
                onClick={() => query.refetch()}
              >
                {tCommon("BTN_RETRY")}
              </Button>
            </div>
          ) : rows.length ? (
            <>
              <p className="mb-2 text-xs text-muted-foreground">
                {t("TXT_TOTAL_ROWS", { count: query.data?.total_rows })}
              </p>
              <Table>
                <TableHeader>
                  <TableRow>
                    {columns.map((column) => (
                      <TableHead key={column}>{column}</TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {rows.map((row, index) => (
                    <TableRow key={index}>
                      {columns.map((column) => (
                        <TableCell key={column} className="max-w-64 truncate">
                          {row[column] ?? ""}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </>
          ) : (
            <p className="rounded-lg border p-4 text-sm text-muted-foreground">
              {t("TXT_PREVIEW_EMPTY")}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
