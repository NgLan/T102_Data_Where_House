"use client";

import { useTranslation } from "react-i18next";
import { Input } from "@/common/components/ui/input";
import {
  NativeSelect,
  NativeSelectOption,
} from "@/common/components/ui/native-select";
import {
  DBML_DATA_TYPE_PRESETS,
  parseDbmlDataType,
} from "@/common/dbml/data-type";
import { DataTypeParameters } from "./DataTypeParameters";

const CUSTOM_DATA_TYPE_VALUE = "__custom__";

interface DataTypeFieldProps {
  value: string;
  isInvalid: boolean;
  onChange: (value: string) => void;
}

/** Cho phép chọn preset DBML hoặc nhập custom type được parser hỗ trợ. */
export function DataTypeField(props: DataTypeFieldProps) {
  const { t } = useTranslation("modeling-dashboard");
  const parsed = parseDbmlDataType(props.value);
  const selectedValue = parsed.preset?.value ?? CUSTOM_DATA_TYPE_VALUE;
  const handleSelectType = (value: string) => {
    if (value === CUSTOM_DATA_TYPE_VALUE) return props.onChange("");
    const preset = DBML_DATA_TYPE_PRESETS.find((item) => item.value === value);
    props.onChange(
      formatDataType(value, preset?.parameterKind ?? "none", parsed.arguments),
    );
  };
  return (
    <div className="space-y-2">
      <NativeSelect
        className="w-full"
        aria-label={t("DATA_TYPE_LABEL")}
        aria-invalid={props.isInvalid}
        value={selectedValue}
        onChange={(event) => handleSelectType(event.target.value)}
      >
        {DBML_DATA_TYPE_PRESETS.map((type) => (
          <NativeSelectOption key={type.value} value={type.value}>
            {type.value}
          </NativeSelectOption>
        ))}
        <NativeSelectOption value={CUSTOM_DATA_TYPE_VALUE}>
          {t("TXT_CUSTOM_DATA_TYPE")}
        </NativeSelectOption>
      </NativeSelect>
      {parsed.preset ? (
        <DataTypeParameters
          preset={parsed.preset}
          argumentsList={parsed.arguments}
          isInvalid={props.isInvalid}
          onChange={props.onChange}
        />
      ) : (
        <Input
          aria-label={t("TXT_CUSTOM_DATA_TYPE")}
          aria-invalid={props.isInvalid}
          value={props.value}
          placeholder={t("DATA_TYPE_CUSTOM_PLACEHOLDER")}
          onChange={(event) => props.onChange(event.target.value)}
        />
      )}
    </div>
  );
}

function formatDataType(
  baseType: string,
  kind: string,
  argumentsList: string[],
): string {
  if (kind === "none" || !argumentsList[0]) return baseType;
  const values =
    kind === "precision-scale"
      ? argumentsList.slice(0, 2)
      : argumentsList.slice(0, 1);
  return `${baseType}(${values.filter(Boolean).join(",")})`;
}
