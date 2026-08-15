import type { DbmlDocument } from './types';
import { emptyTableModel, type DatabaseModel, type TableModel } from './dbml-library-model';
import { mapReference, toReferenceModel } from './dbml-reference-mapper';
import { isSourceId, mapTable, mergeTable, tableId } from './dbml-table-mapper';

/** Ánh xạ raw model của thư viện sang view model độc lập của editor. */
export function fromDatabaseModel(source: unknown): DbmlDocument {
  const model = structuredClone(source) as DatabaseModel;
  return {
    preamble: '',
    tables: model.tables.map(mapTable),
    references: model.refs.map(mapReference),
    sourceModel: model,
  };
}

/** Ánh xạ view model trở lại raw model mà `@dbml/core` công bố. */
export function toDatabaseModel(document: DbmlDocument): DatabaseModel {
  const model = structuredClone(document.sourceModel) as DatabaseModel;
  const tableById = new Map(document.tables.map((table) => [table.id, table]));
  model.tables = model.tables
    .map((table, index) => mergeSourceTable(table, tableById.get(tableId(index))))
    .filter((table): table is TableModel => table !== null);
  document.tables.filter((table) => !isSourceId(table.id))
    .forEach((table) => model.tables.push(mergeTable(emptyTableModel(), table)));
  model.refs = document.references.map(toReferenceModel);
  return model;
}

function mergeSourceTable(
  source: TableModel,
  view: DbmlDocument['tables'][number] | undefined,
): TableModel | null {
  return view ? mergeTable(source, view) : null;
}
