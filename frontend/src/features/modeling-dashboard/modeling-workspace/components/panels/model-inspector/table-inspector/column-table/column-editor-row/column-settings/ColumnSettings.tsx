"use client";

import { useState } from "react";
import { useTranslation } from "react-i18next";
import { ConfirmationDialog } from "@/common/components/ui/ConfirmationDialog";
import { Textarea } from "@/common/components/ui/textarea";
import { isIntegerDbmlType } from "@/features/modeling-dashboard/modeling-workspace/model-document/dbml/data-type";
import type {
  DbmlColumn,
  DbmlDocument,
  DbmlTable,
} from "@/features/modeling-dashboard/modeling-workspace/model-document/dbml/types";
import type { DataModelAction } from "../../../../../../../model-document/reducers/data-model-editor-reducer";
import type { DataModelValidationErrors } from "../../../../../../../model-document/types/data-model-validation-types";
import { getEffectiveColumnConstraints } from "../../../../../../../model-document/utils/column-constraints";
import { CheckExpressionFields } from "./CheckExpressionFields";
import { ColumnSettingCheckbox } from "./ColumnSettingCheckbox";
import { DefaultValueField } from "./DefaultValueField";
import { ForeignKeyField } from "../../../../relationship-inspector/ForeignKeyField";
import { ValidationMessage } from "../../../../shared/ValidationMessage";

interface ColumnSettingsProps {
  document: DbmlDocument;
  table: DbmlTable;
  column: DbmlColumn;
  path: string;
  validationErrors: DataModelValidationErrors;
  mutate: (action: DataModelAction) => void;
}

/** Hiển thị toàn bộ constraint của một cột trong dòng mở rộng. */
export function ColumnSettings(props: ColumnSettingsProps) {
  const { t } = useTranslation(["model-inspector", "common"]);
  const [isIncrementConfirmationOpen, setIncrementConfirmationOpen] =
    useState(false);
  const effective = getEffectiveColumnConstraints(props.table, props.column);
  const update = (patch: Partial<DbmlColumn>) =>
    props.mutate({
      type: "update-column-settings",
      tableId: props.table.id,
      columnId: props.column.id,
      patch,
    });
  const handleChangeIncrement = (isChecked: boolean) => {
    if (isChecked && props.column.defaultValue.trim())
      setIncrementConfirmationOpen(true);
    else update({ isAutoIncrement: isChecked });
  };
  return (
    <div className="space-y-4 border-t bg-muted/30 p-4">
      <label className="block space-y-2 text-xs font-medium text-muted-foreground">
        <span>{t("model-inspector:NOTE_LABEL")}</span>
        <Textarea
          value={props.column.note}
          placeholder={t("model-inspector:COLUMN_NOTE_PLACEHOLDER")}
          onChange={(event) => update({ note: event.target.value })}
        />
      </label>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <ColumnSettingCheckbox
          label={t("model-inspector:PRIMARY_KEY_LABEL")}
          isChecked={props.column.isPrimaryKey}
          onChange={(value) => update({ isPrimaryKey: value })}
        />
        <ColumnSettingCheckbox
          label={t("model-inspector:NOT_NULL_LABEL")}
          isChecked={effective.isNotNull}
          isDisabled={props.column.isPrimaryKey}
          onChange={(value) => update({ isNotNull: value })}
        />
        <ColumnSettingCheckbox
          label={t("model-inspector:UNIQUE_LABEL")}
          isChecked={effective.isUnique}
          isDisabled={
            props.column.isPrimaryKey && !effective.isCompositePrimaryKey
          }
          onChange={(value) => update({ isUnique: value })}
        />
        <ColumnSettingCheckbox
          label={t("model-inspector:AUTO_INCREMENT_LABEL")}
          isChecked={props.column.isAutoIncrement}
          isDisabled={!isIntegerDbmlType(props.column.dataType)}
          onChange={handleChangeIncrement}
        />
      </div>
      <label className="block space-y-2 text-xs font-medium text-muted-foreground">
        <span>{t("model-inspector:DEFAULT_LABEL")}</span>
        <DefaultValueField
          dataType={props.column.dataType}
          value={props.column.defaultValue}
          isInvalid={Boolean(
            props.validationErrors[`${props.path}.defaultValue`],
          )}
          isDisabled={props.column.isAutoIncrement}
          onChange={(value) => update({ defaultValue: value })}
        />
        <ValidationMessage
          code={props.validationErrors[`${props.path}.defaultValue`]}
        />
      </label>
      <CheckExpressionFields
        checks={props.column.checks}
        onChange={(checks) => update({ checks })}
      />
      <ForeignKeyField
        document={props.document}
        table={props.table}
        column={props.column}
        mutate={props.mutate}
      />
      <ConfirmationDialog
        isOpen={isIncrementConfirmationOpen}
        onOpenChange={setIncrementConfirmationOpen}
        title={t("model-inspector:TXT_INCREMENT_CONFLICT_TITLE")}
        content={t("model-inspector:TXT_INCREMENT_CONFLICT_DESCRIPTION")}
        actions={[
          { id: "cancel", label: t("common:BTN_CANCEL"), variant: "outline" },
          {
            id: "confirm",
            label: t("model-inspector:BTN_ENABLE_AND_CLEAR_DEFAULT"),
            variant: "destructive",
            onSelect: () => update({ isAutoIncrement: true, defaultValue: "" }),
          },
        ]}
      />
    </div>
  );
}
