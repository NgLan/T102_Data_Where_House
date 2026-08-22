"use client";

import { useMemo, useState } from "react";
import { ArrowDown, ArrowUp, ArrowUpDown } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { ProjectRequirementResponse } from "@/api";
import { Button } from "@/common/components/ui/button";
import { Empty, EmptyDescription, EmptyHeader, EmptyTitle } from "@/common/components/ui/empty";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/common/components/ui/table";

type SortKey = "requirement" | "type" | "priority";
type SortDirection = "asc" | "desc";
const PRIORITY_ORDER = { HIGH: 0, MEDIUM: 1, LOW: 2 } as const;
const TYPE_ORDER = { BUSINESS: 0, ANALYTICAL: 1, TECHNICAL: 2 } as const;
const collator = new Intl.Collator(undefined, { sensitivity: "base" });

/** Bảng Structured Requirements chỉ đọc với thứ tự nghiệp vụ ổn định. */
export function StructuredRequirementsTable({ items }: { items: ProjectRequirementResponse[] }) {
  const { t } = useTranslation("project-init");
  const [sort, setSort] = useState<{ key: SortKey; direction: SortDirection }>();
  const sortedItems = useMemo(() => [...items].sort(createComparator(sort)), [items, sort]);
  const handleSort = (key: SortKey) => setSort((current) => ({
    key, direction: current?.key === key && current.direction === "asc" ? "desc" : "asc",
  }));
  return (
    <section className="min-w-0 overflow-hidden rounded-lg border">
      <header className="border-b bg-muted/40 px-3 py-2">
        <h3 className="text-sm font-semibold">{t("TXT_ANALYTICAL_REQUIREMENTS_TITLE")}</h3>
        <p className="text-xs text-muted-foreground">{t("TXT_ANALYTICAL_REQUIREMENTS_SUBTITLE")}</p>
      </header>
      {!sortedItems.length ? <Empty className="border-0 py-10"><EmptyHeader>
        <EmptyTitle>{t("TXT_ANALYTICAL_REQUIREMENTS_EMPTY")}</EmptyTitle>
        <EmptyDescription>{t("TXT_ANALYTICAL_REQUIREMENTS_EMPTY_HELP")}</EmptyDescription>
      </EmptyHeader></Empty> : <Table>
        <TableHeader><TableRow>
          <SortableHead label={t("REQUIREMENT_LABEL")} active={sort?.key === "requirement" ? sort.direction : undefined} onClick={() => handleSort("requirement")} />
          <SortableHead label={t("TYPE_LABEL")} active={sort?.key === "type" ? sort.direction : undefined} onClick={() => handleSort("type")} />
          <SortableHead label={t("PRIORITY_LABEL")} active={sort?.key === "priority" ? sort.direction : undefined} onClick={() => handleSort("priority")} />
        </TableRow></TableHeader>
        <TableBody>{sortedItems.map((item) => <TableRow key={item.id}>
          <TableCell className="min-w-64 whitespace-normal"><p className="font-medium">{item.title}</p><p className="text-xs text-muted-foreground">{item.description}</p></TableCell>
          <TableCell>{t(`TXT_TYPE_${item.type}`)}</TableCell>
          <TableCell>{t(`TXT_PRIORITY_${item.priority}`)}</TableCell>
        </TableRow>)}</TableBody>
      </Table>}
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
