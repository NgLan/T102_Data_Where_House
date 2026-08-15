"use client";

import { RuntimeErrorFallback } from "@/common/components/errors/RuntimeErrorFallback";

interface AppErrorProps {
  error: Error & { digest?: string };
  retry: () => void;
}

/** Bắt lỗi render của route gốc và cung cấp thao tác thử lại. */
export default function AppError({ retry }: AppErrorProps) {
  return <RuntimeErrorFallback onRetry={retry} />;
}
