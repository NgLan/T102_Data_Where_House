"use client";

import { Loader2 } from "lucide-react";
import { FormProvider } from "react-hook-form";
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
  onSubmit: (body: CreateProjectRequest) => Promise<unknown>;
}

/** Dialog tạo Project có form schema và server field errors.
 * @param props Trạng thái dialog cùng mutation callback.
 * @returns Dialog tạo Project truy cập được bằng bàn phím.
 */
export function CreateProjectDialog(props: CreateProjectDialogProps) {
  const { t } = useTranslation("project-management");
  const { t: tCommon } = useTranslation("common");
  const { form, handleClose, handleSubmit } = useCreateProjectForm(props);
  const isSubmitting = form.formState.isSubmitting;
  return (
    <Dialog
      open={props.isOpen}
      onOpenChange={(isOpen) =>
        isOpen ? props.onOpenChange(true) : handleClose()
      }
    >
      <DialogContent className="sm:max-w-lg" closeLabel={tCommon("BTN_CLOSE")}>
        <DialogHeader>
          <DialogTitle>{t("TXT_CREATE_TITLE")}</DialogTitle>
          <DialogDescription>{t("TXT_CREATE_DESCRIPTION")}</DialogDescription>
        </DialogHeader>
        <FormProvider {...form}>
          <form onSubmit={handleSubmit} className="space-y-5">
            <CreateProjectFields />
            <DialogFooter className="mx-0 mb-0">
              <Button
                type="button"
                variant="outline"
                onClick={handleClose}
                disabled={isSubmitting}
              >
                {tCommon("BTN_CANCEL")}
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting && (
                  <Loader2 className="animate-spin" aria-hidden />
                )}
                {t(isSubmitting ? "MSG_CREATING" : "BTN_CREATE_ACTION")}
              </Button>
            </DialogFooter>
          </form>
        </FormProvider>
      </DialogContent>
    </Dialog>
  );
}
