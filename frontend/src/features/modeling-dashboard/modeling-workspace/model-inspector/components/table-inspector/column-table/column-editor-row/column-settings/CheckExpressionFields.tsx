"use client";

import { Plus, Trash2 } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import { Input } from "@/common/components/ui/input";

interface CheckExpressionFieldsProps {
  checks: string[];
  onChange: (checks: string[]) => void;
}

/** Chỉnh sửa nhiều DBML check expression của một cột. */
export function CheckExpressionFields(props: CheckExpressionFieldsProps) {
  const { t } = useTranslation("modeling-dashboard");
  const updateCheck = (index: number, value: string) =>
    props.onChange(
      props.checks.map((check, currentIndex) =>
        currentIndex === index ? value : check,
      ),
    );
  const removeCheck = (index: number) =>
    props.onChange(
      props.checks.filter((_, currentIndex) => currentIndex !== index),
    );
  return (
    <fieldset className="space-y-2 rounded-lg border bg-white p-3">
      <div className="flex items-center justify-between">
        <legend className="text-xs font-medium text-slate-600">
          {t("CHECKS_LABEL")}
        </legend>
        <Button
          type="button"
          size="xs"
          variant="outline"
          className="cursor-pointer"
          onClick={() => props.onChange([...props.checks, ""])}
        >
          <Plus />
          {t("BTN_ADD_CHECK")}
        </Button>
      </div>
      {props.checks.map((check, index) => (
        <div key={`${index}-${props.checks.length}`} className="flex gap-2">
          <Input
            aria-label={t("CHECK_EXPRESSION_LABEL", { index: index + 1 })}
            value={check}
            placeholder={t("CHECK_EXPRESSION_PLACEHOLDER")}
            onChange={(event) => updateCheck(index, event.target.value)}
          />
          <Button
            type="button"
            size="icon-sm"
            variant="ghost"
            className="cursor-pointer"
            aria-label={t("BTN_DELETE_CHECK")}
            onClick={() => removeCheck(index)}
          >
            <Trash2 />
          </Button>
        </div>
      ))}
    </fieldset>
  );
}
