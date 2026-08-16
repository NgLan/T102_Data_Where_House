import { Plus, RefreshCw, Search } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import { Input } from "@/common/components/ui/input";
import { cn } from "@/common/lib/utils";

interface ProjectToolbarProps {
  query: string;
  totalCount: number;
  isRefreshing: boolean;
  onQueryChange: (query: string) => void;
  onRefresh: () => void;
  onCreate: () => void;
}

/** Thanh tìm kiếm và action chính của danh sách Project. */
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
          value={props.query}
          onChange={(event) => props.onQueryChange(event.target.value)}
          placeholder={t("SEARCH_PLACEHOLDER")}
          aria-label={t("SEARCH_LABEL")}
        />
      </div>
      <span className="text-sm text-muted-foreground">
        {t("TOTAL_PROJECTS", { count: props.totalCount })}
      </span>
      <Button
        variant="outline"
        size="icon"
        onClick={props.onRefresh}
        disabled={props.isRefreshing}
        aria-label={t("REFRESH")}
        title={t("REFRESH")}
      >
        <RefreshCw className={cn(props.isRefreshing && "animate-spin")} />
      </Button>
      <Button onClick={props.onCreate}>
        <Plus />
        {t("CREATE_PROJECT")}
      </Button>
    </div>
  );
}
