import { Plus, RefreshCw, Search } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import { Input } from "@/common/components/ui/input";
import { cn } from "@/common/lib/utils";

interface ProjectToolbarProps {
  searchQuery: string;
  totalCount: number;
  isRefreshing: boolean;
  onSearchQueryChange: (query: string) => void;
  onRefreshProjects: () => void;
  onCreateProject: () => void;
}

/** Hiển thị tìm kiếm, số lượng và các action của danh sách Project.
 * @param props Trạng thái và callbacks của toolbar.
 * @returns Toolbar responsive cho danh sách Project.
 */
export function ProjectToolbar(props: ProjectToolbarProps) {
  const { t } = useTranslation("project-management");
  return (
    <div className="flex flex-col gap-3 rounded-xl border bg-card p-4 sm:flex-row sm:items-center">
      <div className="relative flex-1">
        <Search
          aria-hidden
          className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
        />
        <Input
          className="pl-9"
          value={props.searchQuery}
          onChange={(event) => props.onSearchQueryChange(event.target.value)}
          placeholder={t("SEARCH_PLACEHOLDER")}
          aria-label={t("SEARCH_LABEL")}
        />
      </div>
      <span className="text-sm text-muted-foreground">
        {t("TXT_TOTAL_PROJECTS", { count: props.totalCount })}
      </span>
      <Button
        variant="outline"
        size="icon"
        onClick={props.onRefreshProjects}
        disabled={props.isRefreshing}
        aria-label={t("BTN_REFRESH")}
        title={t("BTN_REFRESH")}
      >
        <RefreshCw
          className={cn(props.isRefreshing && "animate-spin")}
          aria-hidden
        />
      </Button>
      <Button onClick={props.onCreateProject}>
        <Plus aria-hidden />
        {t("BTN_CREATE_PROJECT")}
      </Button>
    </div>
  );
}
