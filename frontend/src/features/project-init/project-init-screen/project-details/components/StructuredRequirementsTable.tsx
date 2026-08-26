"use client";

import { useMemo, useState } from "react";
import { ArrowDown, ArrowUp, ArrowUpDown, Bot } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { ProjectRequirementResponse } from "@/api";
import { Button } from "@/common/components/ui/button";
import { Badge } from "@/common/components/ui/badge";
import { Empty, EmptyDescription, EmptyHeader, EmptyTitle } from "@/common/components/ui/empty";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/common/components/ui/table";
import { RequirementDeleteAction } from "./RequirementDeleteAction";

type SortKey = "requirement" | "type" | "priority";
type SortDirection = "asc" | "desc";
const PRIORITY_ORDER = { HIGH: 0, MEDIUM: 1, LOW: 2 } as const;
const TYPE_ORDER = { BUSINESS: 0, ANALYTICAL: 1, TECHNICAL: 2 } as const;
const collator = new Intl.Collator(undefined, { sensitivity: "base" });

/** Bảng Structured Requirements chỉ đọc với thứ tự nghiệp vụ ổn định. */
interface StructuredRequirementsTableProps {
  items: ProjectRequirementResponse[];
  canDelete?: boolean;
  isDeleting?: boolean;
  onDelete?: (requirementId: string) => Promise<void>;
  newIds?: readonly string[];
  changedIds?: readonly string[];
  deletedTitles?: readonly string[];
  onOpenChat?: () => void;
  isChatOpen?: boolean;
  hasPendingQuestion?: boolean;
}

export function StructuredRequirementsTable(props: StructuredRequirementsTableProps) {
  const { t } = useTranslation("project-init");
  const [sort, setSort] = useState<{ key: SortKey; direction: SortDirection }>();
  const sortedItems = useMemo(
    () => [...props.items].sort(createComparator(sort)), [props.items, sort],
  );
  const handleSort = (key: SortKey) => setSort((current) => ({
    key, direction: current?.key === key && current.direction === "asc" ? "desc" : "asc",
  }));
  return (
    <section className="flex h-[58vh] min-h-[28rem] min-w-0 flex-col overflow-hidden rounded-lg border">
      <header className="flex items-center justify-between gap-3 border-b bg-muted/40 px-3.5 py-2">
        <div className="min-w-0">
          <h3 className="text-sm font-semibold">{t("TXT_ANALYTICAL_REQUIREMENTS_TITLE")}</h3>
          <p className="text-xs text-muted-foreground">{t("TXT_ANALYTICAL_REQUIREMENTS_SUBTITLE")}</p>
        </div>
        {props.onOpenChat && !props.isChatOpen && (
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={props.onOpenChat}
            className="relative shrink-0 flex items-center gap-1.5 rounded-lg border-primary/30 bg-primary/5 px-2.5 py-1.5 text-xs font-medium text-primary shadow-xs transition-all hover:border-primary/50 hover:bg-primary/10 cursor-pointer"
            title={t("TXT_REQUIREMENT_CHAT_TITLE")}
          >
            <Bot className="size-4 text-primary" />
            <span>{t("TXT_REQUIREMENT_CHAT_TITLE")}</span>
            {props.hasPendingQuestion && (
              <span className="relative flex size-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-amber-400 opacity-75" />
                <span className="relative inline-flex size-2 rounded-full bg-amber-500" />
              </span>
            )}
          </Button>
        )}
      </header>
      {Boolean(props.deletedTitles?.length) && (
        <p className="border-b bg-muted/30 px-3 py-2 text-xs text-muted-foreground">
          {t("TXT_REQUIREMENTS_DELETED", { titles: props.deletedTitles?.join(", ") })}
        </p>
      )}
      {!sortedItems.length ? <Empty className="min-h-0 flex-1 border-0 py-10"><EmptyHeader>
        <EmptyTitle>{t("TXT_ANALYTICAL_REQUIREMENTS_EMPTY")}</EmptyTitle>
        <EmptyDescription>{t("TXT_ANALYTICAL_REQUIREMENTS_EMPTY_HELP")}</EmptyDescription>
      </EmptyHeader></Empty> : <div className="min-h-0 flex-1 overflow-auto"><Table>
        <TableHeader className="sticky top-0 z-10 bg-background"><TableRow>
          <SortableHead label={t("REQUIREMENT_LABEL")} active={sort?.key === "requirement" ? sort.direction : undefined} onClick={() => handleSort("requirement")} />
          <SortableHead label={t("TYPE_LABEL")} active={sort?.key === "type" ? sort.direction : undefined} onClick={() => handleSort("type")} />
          <SortableHead label={t("PRIORITY_LABEL")} active={sort?.key === "priority" ? sort.direction : undefined} onClick={() => handleSort("priority")} />
          {props.canDelete && <TableHead className="w-12"><span className="sr-only">{t("TXT_ACTIONS")}</span></TableHead>}
        </TableRow></TableHeader>
        <TableBody>{sortedItems.map((item) => <TableRow key={item.id}>
          <TableCell className="min-w-64 whitespace-normal"><div className="flex flex-wrap items-center gap-2"><p className="font-medium">{item.title}</p>
            {props.newIds?.includes(item.id) && <Badge>{t("TXT_REQUIREMENT_NEW")}</Badge>}
            {props.changedIds?.includes(item.id) && <Badge variant="secondary">{t("TXT_REQUIREMENT_CHANGED")}</Badge>}
          </div><p className="text-xs text-muted-foreground">{item.description}</p></TableCell>
          <TableCell>{t(`TXT_TYPE_${item.type}`)}</TableCell>
          <TableCell>{t(`TXT_PRIORITY_${item.priority}`)}</TableCell>
          {props.canDelete && <TableCell>
            <RequirementDeleteAction requirementId={item.id} title={item.title}
              isDeleting={Boolean(props.isDeleting)}
              onDelete={props.onDelete as (requirementId: string) => Promise<void>} />
          </TableCell>}
        </TableRow>)}</TableBody>
      </Table></div>}
    </section>
  );
}

function createComparator(sort?: { key: SortKey; direction: SortDirection }) {
  return (left: ProjectRequirementResponse, right: ProjectRequirementResponse) => {
    const selected = sort ? compareBy(sort.key, left, right) * (sort.direction === "asc" ? 1 : -1) : 0;
    return selected || PRIORITY_ORDER[left.priority] - PRIORITY_ORDER[right.priority]
      || TYPE_ORDER[left.type] - TYPE_ORDER[right.type] || collator.compare(left.title, right.title);
  };
}

function compareBy(key: SortKey, left: ProjectRequirementResponse, right: ProjectRequirementResponse) {
  if (key === "priority") return PRIORITY_ORDER[left.priority] - PRIORITY_ORDER[right.priority];
  if (key === "type") return TYPE_ORDER[left.type] - TYPE_ORDER[right.type];
  return collator.compare(left.title, right.title);
}

function SortableHead(props: { label: string; active?: SortDirection; onClick: () => void }) {
  const Icon = props.active === "asc" ? ArrowUp : props.active === "desc" ? ArrowDown : ArrowUpDown;
  return <TableHead><Button type="button" variant="ghost" size="sm" onClick={props.onClick}>
    {props.label}<Icon className="size-3.5" />
  </Button></TableHead>;
}
