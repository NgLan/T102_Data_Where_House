import { useTranslation } from "react-i18next";
import type { DataSourceResponse, UpdateDataSourceColumnRequest } from "@/api";
import { Button } from "@/common/components/ui/button";
import { DataSourceCard } from "./DataSourceCard";
import { DataSourceUpload } from "./DataSourceUpload";

interface DataSourceSectionProps {
  projectId: string;
  sources: DataSourceResponse[];
  canEdit: boolean;
  disabled: boolean;
  loadError: string | null;
  onDelete: (sourceId: string) => void;
  onReload: () => void;
  onUpdate: (sourceId: string, body: UpdateDataSourceColumnRequest) => void;
  onUpload: (files: File[]) => void;
}

/** Section nguồn dữ liệu với trạng thái upload, empty, error và read-only rõ ràng.
 * @param props Danh sách source, quyền truy cập, trạng thái và callback thao tác.
 * @returns Khu vực upload và quản lý toàn bộ Data Source của Project.
 */
export function DataSourceSection(props: DataSourceSectionProps) {
  const { t } = useTranslation("project-init");
  return (
    <section className="space-y-5 rounded-xl border bg-background p-5">
      <div>
        <h2 className="font-semibold">{t("TXT_SOURCE_SECTION_TITLE")}</h2>
        <p className="text-sm text-muted-foreground">
          {t("TXT_SOURCE_SECTION_SUBTITLE")}
        </p>
      </div>
      {!props.canEdit && (
        <p className="rounded-lg bg-muted p-3 text-sm">
          {t("TXT_READ_ONLY_NOTICE")}
        </p>
      )}
      {props.canEdit && (
        <DataSourceUpload
          disabled={props.disabled}
          isUploading={props.disabled}
          onUpload={props.onUpload}
        />
      )}
      {props.loadError ? (
        <div className="rounded-lg border border-destructive/30 p-4">
          <p className="text-sm">{t("TXT_SOURCE_LOAD_ERROR")}</p>
          <Button
            className="mt-3"
            type="button"
            size="sm"
            variant="outline"
            onClick={props.onReload}
          >
            {t("BTN_RETRY")}
          </Button>
        </div>
      ) : props.sources.length ? (
        <div className="space-y-4">
          {props.sources.map((source) => (
            <DataSourceCard
              key={source.id}
              projectId={props.projectId}
              source={source}
              canEdit={props.canEdit}
              disabled={props.disabled}
              onDelete={props.onDelete}
              onUpdate={props.onUpdate}
            />
          ))}
        </div>
      ) : (
        <div className="rounded-lg border border-dashed p-8 text-center">
          <p className="font-medium">{t("TXT_EMPTY_SOURCES_TITLE")}</p>
          <p className="mt-1 text-sm text-muted-foreground">
            {t("TXT_EMPTY_SOURCES_DESCRIPTION")}
          </p>
        </div>
      )}
    </section>
  );
}
