"use client";

import { useTranslation } from "react-i18next";
import { Input } from "@/common/components/ui/input";
import {
  NativeSelect,
  NativeSelectOption,
} from "@/common/components/ui/native-select";
import type { DbmlDocument, DbmlReference } from "@/common/dbml/types";
import type { DataModelAction } from "../../../model-document/reducers/data-model-editor-reducer";
import type { DataModelValidationErrors } from "../../../model-document/types/data-model-validation-types";
import type { RelationshipKind } from "../../../model-document/types/relationship-types";
import {
  dbmlToRelationshipKind,
  relationshipKindToDbml,
} from "../../../model-document/utils/relationship-cardinality";
import { ModelDeleteConfirmationDialog } from "../shared/ModelDeleteConfirmationDialog";
import { ValidationMessage } from "../shared/ValidationMessage";
import { ReferentialActionField } from "./ReferentialActionField";
import { SelectField } from "./SelectField";

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
  const { t } = useTranslation("modeling-dashboard");
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
      <SelectField
        label={t("FROM_TABLE_LABEL")}
        value={reference.fromTable}
        options={document.tables.map((table) => table.name)}
        onChange={(value) => updateTable("from", value)}
      />
      <label className="block space-y-1 text-xs font-medium text-slate-600">
        <span>{t("FROM_COLUMNS_LABEL")}</span>
        <Input
          value={reference.fromColumns.join(", ")}
          onChange={(event) => updateColumns("from", event.target.value)}
        />
      </label>
      <label className="block space-y-1 text-xs font-medium text-slate-600">
        <span>{t("RELATIONSHIP_KIND_LABEL")}</span>
        <NativeSelect
          className="w-full"
          value={dbmlToRelationshipKind(reference.relation)}
          onChange={(event) =>
            update({
              relation: relationshipKindToDbml(
                event.target.value as RelationshipKind,
              ),
            })
          }
        >
          <NativeSelectOption value="many-to-one">
            {t("RELATIONSHIP_MANY_TO_ONE")}
          </NativeSelectOption>
          <NativeSelectOption value="one-to-many">
            {t("RELATIONSHIP_ONE_TO_MANY")}
          </NativeSelectOption>
          <NativeSelectOption value="one-to-one">
            {t("RELATIONSHIP_ONE_TO_ONE")}
          </NativeSelectOption>
          <NativeSelectOption value="many-to-many">
            {t("RELATIONSHIP_MANY_TO_MANY")}
          </NativeSelectOption>
        </NativeSelect>
      </label>
      <SelectField
        label={t("TO_TABLE_LABEL")}
        value={reference.toTable}
        options={document.tables.map((table) => table.name)}
        onChange={(value) => updateTable("to", value)}
      />
      <label className="block space-y-1 text-xs font-medium text-slate-600">
        <span>{t("TO_COLUMNS_LABEL")}</span>
        <Input
          value={reference.toColumns.join(", ")}
          onChange={(event) => updateColumns("to", event.target.value)}
        />
      </label>
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
