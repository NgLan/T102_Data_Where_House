"use client";

import { useState } from "react";
import { Loader2, Trash2 } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import { ConfirmationDialog } from "@/common/components/ui/ConfirmationDialog";

interface ProjectDeleteActionProps {
  projectId: string;
  projectName: string;
  isDeleting: boolean;
  onDeleteProject: (projectId: string) => Promise<void>;
}

/** Hiển thị action và xác nhận xóa một Project.
 * @param props Project đích, trạng thái mutation và callback xóa.
 * @returns Nút xóa cùng confirmation dialog độc lập với nội dung card.
 */
export function ProjectDeleteAction(props: ProjectDeleteActionProps) {
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const { t } = useTranslation("project-management");
  const { t: tCommon } = useTranslation("common");
  const handleDelete = () => props.onDeleteProject(props.projectId)
    .then(() => setIsConfirmOpen(false))
    .catch(() => undefined);
  return <>
    <Button variant="ghost" size="icon" disabled={props.isDeleting}
      onClick={() => setIsConfirmOpen(true)}
      aria-label={t("BTN_DELETE_PROJECT", { name: props.projectName })}>
      {props.isDeleting ? <Loader2 className="animate-spin" /> : <Trash2 />}
    </Button>
    <ConfirmationDialog isOpen={isConfirmOpen} onOpenChange={setIsConfirmOpen}
      title={t("TXT_DELETE_TITLE")}
      content={t("MSG_DELETE_CONFIRM", { name: props.projectName })}
      actions={[
        { id: "cancel", label: tCommon("BTN_CANCEL") },
        { id: "delete", label: props.isDeleting ? t("MSG_DELETING") : tCommon("BTN_DELETE"),
          variant: "destructive", isDisabled: props.isDeleting, shouldClose: false,
          onSelect: () => { void handleDelete(); } },
      ]} />
  </>;
}
