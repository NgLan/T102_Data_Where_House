import { CheckCircle2, XCircle } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Badge } from "@/common/components/ui/badge";
import type { ConnectionStatus } from "../hooks/use-sandbox-connection-test";

interface SandboxConnectionStatusProps {
  latencyMs: number | null;
  status: ConnectionStatus;
}

/** Hiển thị kết quả connection test gần form cấu hình. */
export function SandboxConnectionStatus(props: SandboxConnectionStatusProps) {
  const { t } = useTranslation("sandbox-deployment");
  if (props.status === "success") {
    return (
      <Badge className="border-emerald-200 bg-emerald-50 text-emerald-700" role="status">
        <CheckCircle2 aria-hidden="true" />
        {t("MSG_CONNECTION_SUCCEEDED", { latency: props.latencyMs ?? 0 })}
      </Badge>
    );
  }
  if (props.status === "error") {
    return (
      <Badge variant="destructive" role="status">
        <XCircle aria-hidden="true" />
        {t("MSG_CONNECTION_FAILED")}
      </Badge>
    );
  }
  return <Badge variant="outline">{t("TXT_READY")}</Badge>;
}
