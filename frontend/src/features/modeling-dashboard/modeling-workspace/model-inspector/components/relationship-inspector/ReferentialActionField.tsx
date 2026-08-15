"use client";

import {
  NativeSelect,
  NativeSelectOption,
} from "@/common/components/ui/native-select";
import type { DbmlReference } from "@/common/dbml/types";

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
  const actions = [
    "",
    "cascade",
    "restrict",
    "set null",
    "set default",
    "no action",
  ] as const;
  return (
    <label className="space-y-1 text-xs font-medium text-slate-600">
      <span>{label}</span>
      <NativeSelect
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
                  `REFERENTIAL_ACTION_${action.replaceAll(" ", "_").toUpperCase()}`,
                )
              : t("TXT_NO_ACTION_SETTING")}
          </NativeSelectOption>
        ))}
      </NativeSelect>
    </label>
  );
}
