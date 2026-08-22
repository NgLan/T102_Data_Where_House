"use client";

import { useTranslation } from "react-i18next";
import { Input } from "@/common/components/ui/input";
import {
  NativeSelect,
  NativeSelectOption,
} from "@/common/components/ui/native-select";
import { getDbmlDefaultEditorKind } from "@/features/modeling-dashboard/modeling-workspace/model-document/dbml/default-value";

const INTEGER_INPUT_STEP = 1;

interface DefaultValueFieldProps {
  dataType: string;
  value: string;
  isInvalid: boolean;
  isDisabled?: boolean;
  onChange: (value: string) => void;
}

/** Hiển thị control default tương ứng với kiểu dữ liệu của cột.
 * @param props Kiểu cột, default hiện tại, validation và callback cập nhật.
 * @returns Select boolean hoặc input có ràng buộc số phù hợp.
 */
export function DefaultValueField(props: DefaultValueFieldProps) {
  const { t } = useTranslation("model-inspector");
  const kind = getDbmlDefaultEditorKind(props.dataType);
  if (kind === "boolean") return <BooleanDefaultField {...props} />;
  const isNumeric = kind === "integer" || kind === "decimal";
  const isExpression = props.value.startsWith("`");
  return (
    <Input
      type={isNumeric && !isExpression ? "number" : "text"}
      step={
        kind === "integer"
          ? INTEGER_INPUT_STEP
          : kind === "decimal"
            ? "any"
            : undefined
      }
      inputMode={isNumeric && !isExpression ? "decimal" : "text"}
      aria-label={t("DEFAULT_LABEL")}
      aria-invalid={props.isInvalid}
      disabled={props.isDisabled}
      value={props.value}
      placeholder={t(
        kind === "integer"
          ? "DEFAULT_INTEGER_PLACEHOLDER"
          : kind === "decimal"
            ? "DEFAULT_DECIMAL_PLACEHOLDER"
            : "DEFAULT_PLACEHOLDER",
      )}
      onChange={(event) => props.onChange(event.target.value)}
    />
  );
}

function BooleanDefaultField(props: DefaultValueFieldProps) {
  const { t } = useTranslation("model-inspector");
  return (
    <NativeSelect
      className="w-full"
      aria-label={t("DEFAULT_LABEL")}
      aria-invalid={props.isInvalid}
      disabled={props.isDisabled}
      value={props.value}
      onChange={(event) => props.onChange(event.target.value)}
    >
      <NativeSelectOption value="">{t("TXT_NO_DEFAULT")}</NativeSelectOption>
      <NativeSelectOption value="true">
        {t("TXT_BOOLEAN_TRUE")}
      </NativeSelectOption>
      <NativeSelectOption value="false">
        {t("TXT_BOOLEAN_FALSE")}
      </NativeSelectOption>
    </NativeSelect>
  );
}
