"use client";

import {
  NativeSelect,
  NativeSelectOption,
} from "@/common/components/ui/native-select";

interface SelectFieldProps {
  label: string;
  value: string;
  options: string[];
  onChange: (value: string) => void;
}

export function SelectField({
  label,
  value,
  options,
  onChange,
}: SelectFieldProps) {
  return (
    <label className="block space-y-1 text-xs font-medium text-slate-600">
      <span>{label}</span>
      <NativeSelect
        className="w-full"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        {options.map((option) => (
          <NativeSelectOption key={option} value={option}>
            {option}
          </NativeSelectOption>
        ))}
      </NativeSelect>
    </label>
  );
}
