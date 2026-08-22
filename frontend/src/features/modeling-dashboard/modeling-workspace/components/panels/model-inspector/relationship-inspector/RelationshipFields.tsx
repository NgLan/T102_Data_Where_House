"use client";

import { Input } from "@/common/components/ui/input";
import {
  NativeSelect,
  NativeSelectOption,
} from "@/common/components/ui/native-select";
import type { DbmlReference } from "../../../../model-document/dbml/types";
import type { RelationshipKind } from "../../../../model-document/types/relationship-types";
import {
  dbmlToRelationshipKind,
  relationshipKindToDbml,
} from "../../../../model-document/utils/relationship-cardinality";
import { SelectField } from "./SelectField";

interface EndpointFieldProps {
  label: string;
  columnsLabel: string;
  tableName: string;
  columns: string[];
  tableOptions: string[];
  onChangeTable: (value: string) => void;
  onChangeColumns: (value: string) => void;
}

export function RelationshipEndpointFields(props: EndpointFieldProps) {
  return (
    <>
      <SelectField
        label={props.label}
        value={props.tableName}
        options={props.tableOptions}
        onChange={props.onChangeTable}
      />
      <label className="block space-y-2 text-xs font-medium text-muted-foreground">
        <span>{props.columnsLabel}</span>
        <Input
          value={props.columns.join(", ")}
          onChange={(event) => props.onChangeColumns(event.target.value)}
        />
      </label>
    </>
  );
}

interface RelationshipKindFieldProps {
  label: string;
  reference: DbmlReference;
  labels: Record<RelationshipKind, string>;
  onChange: (relation: DbmlReference["relation"]) => void;
}

export function RelationshipKindField(props: RelationshipKindFieldProps) {
  return (
    <label className="block space-y-2 text-xs font-medium text-muted-foreground">
      <span>{props.label}</span>
      <NativeSelect
        className="w-full"
        value={dbmlToRelationshipKind(props.reference.relation)}
        onChange={(event) =>
          props.onChange(
            relationshipKindToDbml(event.target.value as RelationshipKind),
          )
        }
      >
        {Object.entries(props.labels).map(([kind, label]) => (
          <NativeSelectOption key={kind} value={kind}>
            {label}
          </NativeSelectOption>
        ))}
      </NativeSelect>
    </label>
  );
}
