"use client";

import { Loader2, Trash2 } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import { ConfirmationDialog } from "@/common/components/ui/ConfirmationDialog";

interface RequirementDeleteActionProps {
  requirementId: string;
  title: string;
  isDeleting: boolean;
  onDelete: (requirementId: string) => Promise<void>;
}

/** Xác nhận trước khi xóa một Structured Requirement. */
export function RequirementDeleteAction(props: RequirementDeleteActionProps) {
  const { t } = useTranslation("project-init");
  const { t: tCommon } = useTranslation("common");
  const [isOpen, setIsOpen] = useState(false);
  const handleDelete = () => props.onDelete(props.requirementId)
    .then(() => setIsOpen(false))
    .catch(() => undefined);
  return <>
    <Button type="button" size="icon" variant="ghost"
      disabled={props.isDeleting} aria-label={t("BTN_DELETE_STRUCTURED_REQUIREMENT")}
      onClick={() => setIsOpen(true)}>
      {props.isDeleting ? <Loader2 className="animate-spin" /> : <Trash2 />}
    </Button>
    <ConfirmationDialog isOpen={isOpen} onOpenChange={setIsOpen}
      title={t("TXT_DELETE_REQUIREMENT_TITLE")}
      content={t("MSG_DELETE_REQUIREMENT_CONFIRM", { title: props.title })}
      actions={[
        { id: "cancel", label: tCommon("BTN_CANCEL") },
        { id: "delete", label: tCommon("BTN_DELETE"), variant: "destructive",
          isDisabled: props.isDeleting, shouldClose: false,
          onSelect: () => { void handleDelete(); } },
      ]} />
  </>;
}
