"use client";

import { Loader2, Sparkles } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import type { WorkspaceStatus } from "../../types/modeling-workspace-types";

interface UpdateDataModelButtonProps {
  hasProject: boolean;
  hasExistingModel: boolean;
  status: WorkspaceStatus;
  onGenerate: () => void;
}

/** Tạo model đầu tiên hoặc chủ động sinh lại và ghi đè snapshot hiện hành. */
export function UpdateDataModelButton(props: UpdateDataModelButtonProps) {
  const { t } = useTranslation("modeling-workspace");
  const isGenerating = props.status === "generating";
  const isDisabled =
    !props.hasProject || isGenerating || props.status === "loading";
  const label = props.hasExistingModel
    ? t("BTN_UPDATE_DATA_MODEL")
    : t("BTN_CREATE_INITIAL_MODEL");
  return (
    <Button
      type="button"
      variant="outline"
      size="sm"
      disabled={isDisabled}
      onClick={props.onGenerate}
    >
      {isGenerating ? <Loader2 className="animate-spin" /> : <Sparkles />}
      {label}
    </Button>
  );
}
