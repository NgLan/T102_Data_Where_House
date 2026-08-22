import type { DbmlColumn, DbmlTable } from "./types";
import {
  formatDbmlLibraryDefault,
  parseDefaultToDbmlLibraryModel,
  readDbmlLibraryNote,
} from "./dbml-default-mapper";
import {
  emptyFieldModel,
  type FieldModel,
  type TableModel,
} from "./dbml-library-model";

export function mapDbmlLibraryTableToTable(
  table: TableModel,
  tableIndex: number,
): DbmlTable {
  return {
    id: tableId(tableIndex),
    schemaName: table.schemaName ?? "public",
    name: table.name,
    note: readDbmlLibraryNote(table.note),
    columns: table.fields.map((field, fieldIndex) =>
      mapField(field, tableIndex, fieldIndex),
    ),
    extraStatements: [],
  };
}

export function mergeTableIntoDbmlLibraryModel(
  source: TableModel,
  view: DbmlTable,
): TableModel {
  const fieldById = new Map(view.columns.map((field) => [field.id, field]));
  const tableIndex = sourceIndex(view.id);
  const fields = source.fields
    .map((field, index) => {
      const viewField = fieldById.get(fieldId(tableIndex, index));
      return viewField ? mergeField(field, viewField) : null;
    })
    .filter((field): field is FieldModel => field !== null);
  view.columns
    .filter((field) => !isSourceId(field.id))
    .forEach((field) => fields.push(mergeField(emptyFieldModel(), field)));
  return {
    ...source,
    name: view.name,
    schemaName: view.schemaName === "public" ? null : view.schemaName,
    note: view.note ? { value: view.note } : undefined,
    fields,
  };
}

export function tableId(index: number): string {
  return `source-table-${index}`;
}

export function isSourceId(id: string): boolean {
  return id.startsWith("source-");
}

function mapField(
  field: FieldModel,
  tableIndex: number,
  fieldIndex: number,
): DbmlColumn {
  return {
    id: fieldId(tableIndex, fieldIndex),
    name: field.name,
    dataType: field.type.type_name,
    isPrimaryKey: Boolean(field.pk),
    isNotNull: Boolean(field.not_null),
    isUnique: Boolean(field.unique),
    isAutoIncrement: Boolean(field.increment),
    defaultValue: formatDbmlLibraryDefault(field.dbdefault),
    note: readDbmlLibraryNote(field.note),
    checks: field.checks?.map((check) => check.expression) ?? [],
    extraSettings: [],
  };
}

function mergeField(source: FieldModel, view: DbmlColumn): FieldModel {
  return {
    ...source,
    name: view.name,
    type: { ...source.type, type_name: view.dataType },
    unique: view.isUnique,
    pk: view.isPrimaryKey,
    not_null: view.isNotNull,
    increment: view.isAutoIncrement,
    note: view.note ? { value: view.note } : undefined,
    dbdefault: parseDefaultToDbmlLibraryModel(view.defaultValue),
    checks: view.checks.map((expression) => ({ expression })),
  };
}

function fieldId(tableIndex: number, fieldIndex: number): string {
  return `source-field-${tableIndex}-${fieldIndex}`;
}

function sourceIndex(id: string): number {
  return Number(id.split("-").at(-1));
}
