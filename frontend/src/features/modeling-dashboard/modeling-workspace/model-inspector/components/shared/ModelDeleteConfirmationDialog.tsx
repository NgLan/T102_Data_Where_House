"use client";

import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import { ConfirmationDialog } from "@/common/components/ui/confirmation-dialog";

interface ModelDeleteConfirmationDialogProps {
  title: string;
  description: string;
  onConfirm: () => void;
}

/** Yêu cầu xác nhận trước khi xóa một phần tử Data Model.
 * @param props Nội dung cảnh báo và callback xóa.
 * @returns AlertDialog dùng primitive shadcn hiện có.
 */
export function ModelDeleteConfirmationDialog({
  title,
  description,
  onConfirm,
}: ModelDeleteConfirmationDialogProps) {
  const { t } = useTranslation("common");
  return (
    <ConfirmationDialog
      trigger={
        <Button type="button" variant="destructive" size="sm">
          {t("BTN_DELETE")}
        </Button>
      }
      title={title}
      content={description}
      actions={[
        { id: "cancel", label: t("BTN_CANCEL"), variant: "outline" },
        {
          id: "delete",
          label: t("BTN_DELETE"),
          variant: "destructive",
          onSelect: onConfirm,
        },
      ]}
    />
  );
}
