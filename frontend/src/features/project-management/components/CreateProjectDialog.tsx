"use client";

import { Loader2 } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { CreateProjectRequest } from "@/api";
import { Button } from "@/common/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/common/components/ui/dialog";
import { useCreateProjectForm } from "../hooks/use-create-project-form";
import { CreateProjectFields } from "./CreateProjectFields";

interface CreateProjectDialogProps {
  isOpen: boolean;
  onOpenChange: (isOpen: boolean) => void;
  onSubmit: (body: CreateProjectRequest) => Promise<void>;
}

/** Dialog tạo Project có Zod và ánh xạ validation details từ Backend. */
export function CreateProjectDialog({
  isOpen,
  onOpenChange,
  onSubmit,
}: CreateProjectDialogProps) {
  const { t } = useTranslation("project-management");
  const form = useCreateProjectForm({ onOpenChange, onSubmit, translateError: t });
  return (
    <Dialog
      open={isOpen}
      onOpenChange={(open) => (open ? onOpenChange(true) : form.handleClose())}
    >
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{t("CREATE_TITLE")}</DialogTitle>
          <DialogDescription>{t("CREATE_DESCRIPTION")}</DialogDescription>
        </DialogHeader>
        <form onSubmit={form.handleSubmit} className="space-y-4">
          <CreateProjectFields values={form.values} errors={form.errors}
            onFieldChange={form.handleFieldChange} />
          <DialogFooter className="mx-0 mb-0">
            <Button
              type="button"
              variant="outline"
              onClick={form.handleClose}
              disabled={form.isSubmitting}
            >
              {t("CANCEL")}
            </Button>
            <Button type="submit" disabled={form.isSubmitting}>
              {form.isSubmitting && <Loader2 className="animate-spin" />}
              {t(form.isSubmitting ? "CREATING" : "CREATE_ACTION")}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
