"use client";

import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/common/components/ui/dialog";
import { Textarea } from "@/common/components/ui/textarea";

interface ColumnOptionsDialogProps {
  columnName: string;
  options: string[];
  disabled: boolean;
  onClose: () => void;
  onSave: (options: string[]) => void;
}

/** Chỉnh danh mục OPTION, mỗi dòng là một giá trị.
 * @param props Trạng thái dialog, danh sách option và callback lưu/đóng.
 * @returns Dialog chỉnh các giá trị hợp lệ của cột OPTION.
 */
export function ColumnOptionsDialog(props: ColumnOptionsDialogProps) {
  const { t } = useTranslation("project-init");
  const [value, setValue] = useState(() => props.options.join("\n"));
  const normalized = Array.from(
    new Set(
      value
        .split("\n")
        .map((item) => item.trim())
        .filter(Boolean),
    ),
  );
  return (
    <Dialog open onOpenChange={(open) => !open && props.onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {t("TXT_OPTIONS_DIALOG_TITLE", { column: props.columnName })}
          </DialogTitle>
          <DialogDescription>
            {t("TXT_OPTIONS_DIALOG_DESCRIPTION")}
          </DialogDescription>
        </DialogHeader>
        <Textarea
          rows={8}
          value={value}
          disabled={props.disabled}
          placeholder={t("PH_COLUMN_OPTIONS")}
          onChange={(event) => setValue(event.target.value)}
        />
        <DialogFooter>
          <Button type="button" variant="outline" onClick={props.onClose}>
            {t("BTN_CANCEL")}
          </Button>
          <Button
            type="button"
            disabled={props.disabled || !normalized.length}
            onClick={() => props.onSave(normalized)}
          >
            {t("BTN_SAVE_OPTIONS")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
