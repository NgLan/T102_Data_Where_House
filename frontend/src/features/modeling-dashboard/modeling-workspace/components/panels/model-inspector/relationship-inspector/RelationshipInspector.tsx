"use client";

import { useTranslation } from "react-i18next";
import type {
  DbmlDocument,
  DbmlReference,
} from "@/features/modeling-dashboard/modeling-workspace/model-document/dbml/types";
import type { DataModelAction } from "../../../../model-document/reducers/data-model-editor-reducer";
import type { DataModelValidationErrors } from "../../../../model-document/types/data-model-validation-types";
import { ModelDeleteConfirmationDialog } from "../shared/ModelDeleteConfirmationDialog";
import { ValidationMessage } from "../shared/ValidationMessage";
import { ReferentialActionField } from "./ReferentialActionField";
import {
  RelationshipEndpointFields,
  RelationshipKindField,
} from "./RelationshipFields";

interface RelationshipInspectorProps {
  document: DbmlDocument;
  reference: DbmlReference;
  referenceIndex: number;
  validationErrors: DataModelValidationErrors;
  mutate: (action: DataModelAction) => void;
  onDeleted: () => void;
}

/** Chỉnh endpoint, composite columns và cardinality của relationship.
 * @param props Document, relationship và reducer command.
 * @returns Form relationship trong dock inspector.
 */
export function RelationshipInspector(props: RelationshipInspectorProps) {
  const { document, reference, mutate, onDeleted } = props;
  const { t } = useTranslation("model-inspector");
  const tableOptions = document.tables.map((table) => table.name);
  const update = (patch: Partial<DbmlReference>) =>
    mutate({ type: "update-reference", reference: { ...reference, ...patch } });
  const updateTable = (side: "from" | "to", tableName: string) => {
    const table = document.tables.find((item) => item.name === tableName);
    const column = table?.columns[0]?.name ?? "";
    update(
      side === "from"
        ? {
            fromSchema: table?.schemaName ?? "",
            fromTable: tableName,
            fromColumn: column,
            fromColumns: column ? [column] : [],
          }
        : {
            toSchema: table?.schemaName ?? "",
            toTable: tableName,
            toColumn: column,
            toColumns: column ? [column] : [],
          },
    );
  };
  const updateColumns = (side: "from" | "to", value: string) => {
    const columns = value
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
    update(
      side === "from"
        ? { fromColumns: columns, fromColumn: columns[0] ?? "" }
        : { toColumns: columns, toColumn: columns[0] ?? "" },
    );
  };
  return (
    <div className="space-y-4 p-4">
      <RelationshipEndpointFields
        label={t("FROM_TABLE_LABEL")}
        columnsLabel={t("FROM_COLUMNS_LABEL")}
        tableName={reference.fromTable}
        columns={reference.fromColumns}
        tableOptions={tableOptions}
        onChangeTable={(value) => updateTable("from", value)}
        onChangeColumns={(value) => updateColumns("from", value)}
      />
      <RelationshipKindField
        label={t("RELATIONSHIP_KIND_LABEL")}
        reference={reference}
        labels={{
          "many-to-one": t("TXT_RELATIONSHIP_MANY_TO_ONE"),
          "one-to-many": t("TXT_RELATIONSHIP_ONE_TO_MANY"),
          "one-to-one": t("TXT_RELATIONSHIP_ONE_TO_ONE"),
          "many-to-many": t("TXT_RELATIONSHIP_MANY_TO_MANY"),
        }}
        onChange={(relation) => update({ relation })}
      />
      <RelationshipEndpointFields
        label={t("TO_TABLE_LABEL")}
        columnsLabel={t("TO_COLUMNS_LABEL")}
        tableName={reference.toTable}
        columns={reference.toColumns}
        tableOptions={tableOptions}
        onChangeTable={(value) => updateTable("to", value)}
        onChangeColumns={(value) => updateColumns("to", value)}
      />
      <ValidationMessage
        code={
          props.validationErrors[`references.${props.referenceIndex}.columns`]
        }
      />
      <ValidationMessage
        code={props.validationErrors[`references.${props.referenceIndex}`]}
      />
      <div className="grid gap-3 sm:grid-cols-2">
        <ReferentialActionField
          label={t("ON_DELETE_LABEL")}
          value={reference.onDelete ?? ""}
          onChange={(onDelete) => update({ onDelete })}
          t={t}
        />
        <ReferentialActionField
          label={t("ON_UPDATE_LABEL")}
          value={reference.onUpdate ?? ""}
          onChange={(onUpdate) => update({ onUpdate })}
          t={t}
        />
      </div>
      <ModelDeleteConfirmationDialog
        title={t("TXT_DELETE_RELATIONSHIP")}
        description={t("TXT_DELETE_RELATIONSHIP_DESCRIPTION")}
        onConfirm={() => {
          mutate({ type: "remove-reference", referenceId: reference.id });
          onDeleted();
        }}
      />
    </div>
  );
}
