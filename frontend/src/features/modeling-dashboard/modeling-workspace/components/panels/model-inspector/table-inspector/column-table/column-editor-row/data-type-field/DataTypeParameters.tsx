"use client";

import { useTranslation } from "react-i18next";
import { Input } from "@/common/components/ui/input";
import type { DbmlDataTypePreset } from "@/features/modeling-dashboard/modeling-workspace/model-document/dbml/data-type";

interface DataTypeParametersProps {
  preset: DbmlDataTypePreset;
  argumentsList: string[];
  isInvalid: boolean;
  onChange: (value: string) => void;
}

/** Hiển thị tham số số nguyên phù hợp với preset data type. */
export function DataTypeParameters(props: DataTypeParametersProps) {
  const { t } = useTranslation("model-inspector");
  if (props.preset.parameterKind === "none") return null;
  const handleChangeArgument = (index: number, value: string) => {
    if (!/^\d*$/.test(value)) return;
    const next = [...props.argumentsList];
    next[index] = value;
    props.onChange(formatType(props.preset, next));
  };
  const labels =
    props.preset.parameterKind === "precision-scale"
      ? (["DATA_TYPE_PRECISION_LABEL", "DATA_TYPE_SCALE_LABEL"] as const)
      : ([
          props.preset.parameterKind === "length"
            ? "DATA_TYPE_LENGTH_LABEL"
            : "DATA_TYPE_PRECISION_LABEL",
        ] as const);
  return (
    <div className="grid grid-cols-2 gap-2">
      {labels.map((label, index) => (
        <Input
          key={label}
          type="text"
          inputMode="numeric"
          pattern="[0-9]*"
          aria-label={t(label)}
          aria-invalid={props.isInvalid}
          disabled={index === 1 && !props.argumentsList[0]}
          placeholder={t(label)}
          value={props.argumentsList[index] ?? ""}
          onChange={(event) => handleChangeArgument(index, event.target.value)}
        />
      ))}
    </div>
  );
}

function formatType(
  preset: DbmlDataTypePreset,
  argumentsList: string[],
): string {
  if (!argumentsList[0]) return preset.value;
  const count = preset.parameterKind === "precision-scale" ? 2 : 1;
  return `${preset.value}(${argumentsList.slice(0, count).filter(Boolean).join(",")})`;
}
