import type { DbmlDocument } from './types';
import { emptyTableModel, type DatabaseModel, type TableModel } from './dbml-library-model';
import {
  mapDbmlLibraryReferenceToReference,
  mapReferenceToDbmlLibraryModel,
} from './dbml-reference-mapper';
import {
  isSourceId,
  mapDbmlLibraryTableToTable,
  mergeTableIntoDbmlLibraryModel,
  tableId,
} from './dbml-table-mapper';

/** Ánh xạ raw model của thư viện sang view model độc lập của editor. */
export function mapDbmlLibraryModelToDocument(source: unknown): DbmlDocument {
  const model = structuredClone(source) as DatabaseModel;
  return {
    preamble: '',
    tables: model.tables.map(mapDbmlLibraryTableToTable),
    references: model.refs.map(mapDbmlLibraryReferenceToReference),
    sourceModel: model,
  };
}

/** Ánh xạ view model trở lại raw model mà `@dbml/core` công bố. */
export function mapDocumentToDbmlLibraryModel(document: DbmlDocument): DatabaseModel {
  const model = structuredClone(document.sourceModel) as DatabaseModel;
  const tableById = new Map(document.tables.map((table) => [table.id, table]));
  model.tables = model.tables
    .map((table, index) => mergeSourceTable(table, tableById.get(tableId(index))))
    .filter((table): table is TableModel => table !== null);
  document.tables.filter((table) => !isSourceId(table.id))
    .forEach((table) => model.tables.push(mergeTableIntoDbmlLibraryModel(emptyTableModel(), table)));
  model.refs = document.references.map(mapReferenceToDbmlLibraryModel);
  return model;
}

function mergeSourceTable(
  source: TableModel,
  view: DbmlDocument['tables'][number] | undefined,
): TableModel | null {
  return view ? mergeTableIntoDbmlLibraryModel(source, view) : null;
}
