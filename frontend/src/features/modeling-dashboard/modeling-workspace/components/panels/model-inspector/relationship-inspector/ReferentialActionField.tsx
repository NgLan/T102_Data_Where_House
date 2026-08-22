"use client";

import {
  NativeSelect,
  NativeSelectOption,
} from "@/common/components/ui/native-select";
import type { DbmlReference } from "@/features/modeling-dashboard/modeling-workspace/model-document/dbml/types";
import { Field, FieldLabel } from "@/common/components/ui/field";

interface ReferentialActionFieldProps {
  label: string;
  value: string;
  onChange: (value: DbmlReference["onDelete"]) => void;
  t: (key: string) => string;
}

export function ReferentialActionField({
  label,
  value,
  onChange,
  t,
}: ReferentialActionFieldProps) {
  const id = `referential-${label.toLocaleLowerCase().replaceAll(" ", "-")}`;
  const actions = [
    "",
    "cascade",
    "restrict",
    "set null",
    "set default",
    "no action",
  ] as const;
  return (
    <Field>
      <FieldLabel htmlFor={id} className="text-xs">{label}</FieldLabel>
      <NativeSelect
        id={id}
        className="w-full"
        value={value}
        onChange={(event) =>
          onChange(event.target.value as DbmlReference["onDelete"])
        }
      >
        {actions.map((action) => (
          <NativeSelectOption key={action} value={action}>
            {action
              ? t(
                  `TXT_REFERENTIAL_ACTION_${action.replaceAll(" ", "_").toUpperCase()}`,
                )
              : t("TXT_NO_ACTION_SETTING")}
          </NativeSelectOption>
        ))}
      </NativeSelect>
    </Field>
  );
}
