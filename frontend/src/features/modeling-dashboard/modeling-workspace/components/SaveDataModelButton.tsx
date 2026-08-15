"use client";

import { Loader2, Save } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/common/components/ui/tooltip";
import type { WorkspaceStatus } from "../types/modeling-workspace-types";

interface SaveDataModelButtonProps {
  canSave: boolean;
  isDirty: boolean;
  status: WorkspaceStatus;
  onSave: () => void;
}

/** Lưu DBML hiện tại và công bố phím tắt Ctrl+S qua tooltip. */
export function SaveDataModelButton(props: SaveDataModelButtonProps) {
  const { t } = useTranslation("modeling-dashboard");
  const isDisabled =
    !props.canSave || !props.isDirty || props.status === "saving";
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <span className="inline-flex">
          <Button
            type="button"
            size="sm"
            disabled={isDisabled}
            onClick={props.onSave}
          >
            {props.status === "saving" ? (
              <Loader2 className="animate-spin" />
            ) : (
              <Save />
            )}
            {t("BTN_SAVE")}
          </Button>
        </span>
      </TooltipTrigger>
      <TooltipContent>{t("TXT_SAVE_SHORTCUT")}</TooltipContent>
    </Tooltip>
  );
}
