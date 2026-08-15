"use client";

import { Checkbox } from "@/common/components/ui/checkbox";
import { useId } from "react";

interface ColumnSettingCheckboxProps {
  label: string;
  isChecked: boolean;
  isDisabled?: boolean;
  onChange: (isChecked: boolean) => void;
}

/** Checkbox constraint có label truy cập được và vùng bấm không chồng lấn. */
export function ColumnSettingCheckbox(props: ColumnSettingCheckboxProps) {
  const id = useId();
  return (
    <label
      htmlFor={id}
      className="flex cursor-pointer items-center gap-2 rounded-lg border bg-white p-3 hover:bg-slate-50"
    >
      <Checkbox
        id={id}
        checked={props.isChecked}
        disabled={props.isDisabled}
        onCheckedChange={(value) => props.onChange(value === true)}
      />
      <span className="text-xs font-medium text-slate-700">{props.label}</span>
    </label>
  );
}
