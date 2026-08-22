import { TriangleAlert } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/common/components/ui/empty";
import { useAppNotification } from "@/common/notifications";

interface SandboxDeploymentLoadErrorProps {
  errorCode: string;
  onRetry: () => void;
}

/** Hiển thị lỗi initial load và cho phép tải lại cả config lẫn DDL. */
export function SandboxDeploymentLoadError(props: SandboxDeploymentLoadErrorProps) {
  const { t } = useTranslation("sandbox-deployment");
  const { t: tCommon } = useTranslation("common");
  const { getErrorMessage } = useAppNotification();
  return (
    <Empty className="min-h-[420px] border">
      <EmptyHeader>
        <EmptyMedia variant="icon"><TriangleAlert /></EmptyMedia>
        <EmptyTitle>{t("TXT_LOAD_ERROR_TITLE")}</EmptyTitle>
        <EmptyDescription>{getErrorMessage(props.errorCode)}</EmptyDescription>
      </EmptyHeader>
      <EmptyContent>
        <Button type="button" variant="outline" onClick={props.onRetry}>
          {tCommon("BTN_RETRY")}
        </Button>
      </EmptyContent>
    </Empty>
  );
}
