"use client";

import { useCallback, useState } from "react";
import { useTranslation } from "react-i18next";
import type { DataSourcePreviewResponse } from "@/api";
import { Button } from "@/common/components/ui/button";
import { Skeleton } from "@/common/components/ui/skeleton";
import { getDataSourcePreview } from "../services/data-source-service";

interface DataPreviewProps {
  projectId: string;
  sourceId: string;
}

/** Preview CSV đọc lười; không dùng dữ liệu sample hoặc parser phía client.
 * @param props ID Project và Data Source cần xem trước.
 * @returns Bảng preview hoặc trạng thái tải/lỗi tương ứng.
 */
export function DataPreview({ projectId, sourceId }: DataPreviewProps) {
  const { t } = useTranslation("project-init");
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [preview, setPreview] = useState<DataSourcePreviewResponse | null>(
    null,
  );
  const load = useCallback(async () => {
    setIsLoading(true);
    setHasError(false);
    try {
      setPreview(await getDataSourcePreview(projectId, sourceId));
    } catch {
      setHasError(true);
    } finally {
      setIsLoading(false);
    }
  }, [projectId, sourceId]);
  const toggle = () => {
    const next = !isOpen;
    setIsOpen(next);
    if (next && !preview) void load();
  };
  const rows = preview?.rows ?? [];
  const columns = rows[0] ? Object.keys(rows[0]) : [];
  return (
    <div>
      <Button type="button" size="sm" variant="outline" onClick={toggle}>
        {isOpen ? t("BTN_HIDE_PREVIEW") : t("BTN_SHOW_PREVIEW")}
      </Button>
      {isOpen && (
        <div className="mt-3">
          {isLoading && <Skeleton className="h-32 w-full" />}
          {hasError && (
            <div className="rounded-lg border border-destructive/30 p-4 text-sm">
              <p>{t("TXT_PREVIEW_ERROR")}</p>
              <Button
                className="mt-2"
                type="button"
                size="sm"
                variant="outline"
                onClick={() => void load()}
              >
                {t("BTN_RETRY")}
              </Button>
            </div>
          )}
          {!isLoading && !hasError && preview && (
            <>
              <p className="mb-2 text-xs text-muted-foreground">
                {t("TXT_TOTAL_ROWS", { count: preview.total_rows })}
              </p>
              {rows.length ? (
                <div className="overflow-x-auto rounded-lg border">
                  <table className="w-full whitespace-nowrap text-left text-xs">
                    <thead className="bg-muted/50">
                      <tr>
                        {columns.map((column) => (
                          <th key={column} className="px-3 py-2 font-medium">
                            {column}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {rows.map((row, index) => (
                        <tr key={index} className="border-t">
                          {columns.map((column) => (
                            <td
                              key={column}
                              className="max-w-64 truncate px-3 py-2"
                            >
                              {row[column] ?? "—"}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="rounded-lg border p-4 text-sm text-muted-foreground">
                  {t("TXT_PREVIEW_EMPTY")}
                </p>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
