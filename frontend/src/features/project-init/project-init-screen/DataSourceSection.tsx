import { DatabaseZap } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { DataSourceResponse } from "@/api";
import type { SourceCoverageBatchResponse } from "@/api";
import { cn } from "@/common/lib/utils";
import { Button } from "@/common/components/ui/button";
import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/common/components/ui/empty";
import { DataSourceCard } from "./data-sources/components/DataSourceCard";
import { DataSourceUpload } from "./data-sources/components/DataSourceUpload";
import { SourceCoverageWarning } from "./data-sources/components/SourceCoverageWarning";

interface DataSourceSectionProps {
  projectId: string;
  sources: DataSourceResponse[];
  canEdit: boolean;
  disabled: boolean;
  hasError: boolean;
  onDelete: (sourceId: string) => void;
  onReload: () => void;
  onUpload: (files: File[]) => void;
  sourceCoverageBatch: SourceCoverageBatchResponse | null;
  sourceRevision: number;
  isSourceCoverageStale: boolean;
  isRecheckingCoverage: boolean;
  pendingCoverageItemIds: ReadonlySet<string>;
  coverageItemErrors: ReadonlySet<string>;
  onResolveCoverage: Parameters<typeof SourceCoverageWarning>[0]["onResolve"];
  onRecheckCoverage: Parameters<typeof SourceCoverageWarning>[0]["onRecheck"];
  onEditRequirement: () => void;
}

/** Khu vực upload và danh sách Data Source. */
export function DataSourceSection(props: DataSourceSectionProps) {
  const { t } = useTranslation("project-init");
  const { t: tCommon } = useTranslation("common");
  return (
    <section className={cn(
      "space-y-5 rounded-xl border bg-background p-5",
      props.sourceCoverageBatch && "border-amber-400 bg-amber-50/50 dark:bg-amber-950/20",
    )}>
      <header>
        <h2 className="font-semibold">{t("TXT_SOURCE_SECTION_TITLE")}</h2>
        <p className="text-sm text-muted-foreground">
          {t("TXT_SOURCE_SECTION_SUBTITLE")}
        </p>
      </header>
      {props.sourceCoverageBatch && (
        <SourceCoverageWarning
          batch={props.sourceCoverageBatch}
          expectedSourceRevision={props.sourceRevision}
          disabled={props.disabled || !props.canEdit}
          isStale={props.isSourceCoverageStale}
          isRechecking={props.isRecheckingCoverage}
          onResolve={props.onResolveCoverage}
          onRecheck={props.onRecheckCoverage}
          pendingItemIds={props.pendingCoverageItemIds}
          itemErrors={props.coverageItemErrors}
          onUploadRequest={() => document.getElementById("source-upload")?.scrollIntoView({ behavior: "smooth" })}
          onEditRequirement={props.onEditRequirement}
        />
      )}
      {!props.canEdit && (
        <p className="rounded-lg bg-muted p-3 text-sm">
          {t("TXT_READ_ONLY_NOTICE")}
        </p>
      )}
      {props.canEdit && (
        <div id="source-upload">
          <DataSourceUpload
            disabled={props.disabled}
            remainingSlots={Math.max(0, 20 - props.sources.length)}
            onUpload={props.onUpload}
          />
        </div>
      )}
      {props.hasError ? (
        <div className="rounded-lg border border-destructive/30 p-4">
          <p className="text-sm">{t("TXT_SOURCE_LOAD_ERROR")}</p>
          <Button
            className="mt-3"
            type="button"
            size="sm"
            variant="outline"
            onClick={props.onReload}
          >
            {tCommon("BTN_RETRY")}
          </Button>
        </div>
      ) : props.sources.length ? (
        <div className="space-y-3">
          {props.sources.map((source) => (
            <DataSourceCard
              key={source.id}
              projectId={props.projectId}
              source={source}
              canEdit={props.canEdit}
              disabled={props.disabled}
              onDelete={props.onDelete}
            />
          ))}
        </div>
      ) : (
        <Empty className="border">
          <EmptyHeader>
            <EmptyMedia variant="icon">
              <DatabaseZap />
            </EmptyMedia>
            <EmptyTitle>{t("TXT_EMPTY_SOURCES_TITLE")}</EmptyTitle>
            <EmptyDescription>
              {t("TXT_EMPTY_SOURCES_DESCRIPTION")}
            </EmptyDescription>
          </EmptyHeader>
        </Empty>
      )}
    </section>
  );
}
