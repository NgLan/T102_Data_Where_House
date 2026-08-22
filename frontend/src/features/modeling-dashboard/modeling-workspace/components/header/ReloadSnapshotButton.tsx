"use client";

import { RotateCcw } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import { ConfirmationDialog } from "@/common/components/ui/ConfirmationDialog";

interface ReloadSnapshotButtonProps {
  isDirty: boolean;
  isDisabled: boolean;
  onReload: () => void;
}

/** Tải revision mới nhất và xác nhận trước khi bỏ draft chưa lưu.
 * @param props Dirty state, disabled state và callback tải lại.
 * @returns Nút tải lại hoặc dialog xác nhận tương ứng.
 */
export function ReloadSnapshotButton(props: ReloadSnapshotButtonProps) {
  const { t } = useTranslation(["modeling-workspace", "common"]);
  if (!props.isDirty)
    return (
      <Button
        type="button"
        variant="outline"
        size="sm"
        disabled={props.isDisabled}
        onClick={props.onReload}
      >
        <RotateCcw />
        {t("modeling-workspace:BTN_RELOAD_LATEST")}
      </Button>
    );
  return (
    <ConfirmationDialog
      trigger={
        <Button
          type="button"
          variant="outline"
          size="sm"
          disabled={props.isDisabled}
        >
          <RotateCcw />
          {t("modeling-workspace:BTN_RELOAD_LATEST")}
        </Button>
      }
      title={t("modeling-workspace:TXT_DISCARD_TITLE")}
      content={t("modeling-workspace:TXT_DISCARD_DESCRIPTION")}
      actions={[
        { id: "cancel", label: t("common:BTN_CANCEL"), variant: "outline" },
        {
          id: "reload",
          label: t("modeling-workspace:BTN_RELOAD_LATEST"),
          onSelect: props.onReload,
        },
      ]}
    />
  );
}
