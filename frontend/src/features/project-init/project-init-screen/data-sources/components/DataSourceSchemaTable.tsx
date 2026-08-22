import { useTranslation } from "react-i18next";
import type { DataSourceColumnResponse, DataSourceTableResponse } from "@/api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/common/components/ui/table";

/** Metadata suy luận chỉ đọc; không trình bày candidate như constraint chính thức. */
export function DataSourceSchemaTable({ table }: { table: DataSourceTableResponse }) {
  const { t } = useTranslation("project-init");
  return <section className="overflow-hidden rounded-lg border">
    <h4 className="border-b bg-muted/50 px-3 py-2 text-sm font-medium">{table.name}</h4>
    <Table><TableHeader><TableRow>
      <TableHead>{t("COLUMN_NAME_LABEL")}</TableHead>
      <TableHead>{t("COLUMN_TYPE_LABEL")}</TableHead>
      <TableHead>{t("COLUMN_PROPERTIES_LABEL")}</TableHead>
    </TableRow></TableHeader><TableBody>{table.columns.map((column) => <TableRow key={column.name}>
      <TableCell className="font-mono text-xs">{column.name}</TableCell>
      <TableCell>{column.data_type}</TableCell>
      <TableCell className="whitespace-normal text-xs text-muted-foreground">{propertyText(column, t)}</TableCell>
    </TableRow>)}</TableBody></Table>
  </section>;
}

function propertyText(column: DataSourceColumnResponse, t: (key: string) => string): string {
  const properties = [column.nullable && t("TXT_NULLABLE"),
    column.is_unique_candidate && t("TXT_UNIQUE_CANDIDATE"),
    column.is_key_candidate && t("TXT_KEY_CANDIDATE")].filter(Boolean);
  if (column.data_type === "CATEGORY") {
    const values = (column.distinct_values ?? []).filter((value): value is string => typeof value === "string");
    if (values.length) properties.push(`${t("TXT_CATEGORY_VALUES")}: ${values.join(", ")}`);
  }
  return properties.join(" · ") || t("TXT_NO_PROPERTIES");
}
