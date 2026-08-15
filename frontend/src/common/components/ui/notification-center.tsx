"use client";

import { CircleAlert, CircleCheck, TriangleAlert, X } from "lucide-react";
import { Toast } from "radix-ui";
import { useTranslation } from "react-i18next";
import { cn } from "@/common/lib/utils";
import {
  type NotificationType,
  useNotificationStore,
} from "@/common/stores/use-notification-store";

/** Hiển thị hàng đợi toast toàn cục và tự đóng từng thông báo. */
export function NotificationCenter() {
  const { t } = useTranslation("common");
  const notifications = useNotificationStore((state) => state.notifications);
  const dismiss = useNotificationStore((state) => state.dismiss);
  return (
    <Toast.Provider duration={5000} swipeDirection="right">
      {notifications.map((notification) => {
        const Icon = notificationIcon(notification.type);
        return (
          <Toast.Root
            key={notification.id}
            open
            onOpenChange={(isOpen) => !isOpen && dismiss(notification.id)}
            className={cn(
              "grid grid-cols-[auto_1fr_auto] items-start gap-x-3 rounded-lg border bg-white p-4 shadow-lg",
              "data-[state=closed]:animate-out data-[state=open]:animate-in data-[swipe=end]:translate-x-[var(--radix-toast-swipe-end-x)]",
              notificationBorder(notification.type),
            )}
          >
            <Icon
              className={cn(
                "mt-0.5 size-5",
                notificationColor(notification.type),
              )}
            />
            <div className="min-w-0">
              <Toast.Title className="text-sm font-semibold text-slate-900">
                {notification.title}
              </Toast.Title>
              <Toast.Description className="mt-1 text-sm text-slate-600">
                {notification.message}
              </Toast.Description>
            </div>
            <Toast.Close
              aria-label={t("BTN_CLOSE")}
              className="cursor-pointer rounded p-1 text-slate-500 hover:bg-slate-100 hover:text-slate-900"
            >
              <X className="size-4" />
            </Toast.Close>
          </Toast.Root>
        );
      })}
      <Toast.Viewport className="fixed right-4 top-4 z-[100] flex w-[min(420px,calc(100vw-2rem))] flex-col gap-2 outline-none" />
    </Toast.Provider>
  );
}

/** Chọn icon theo mức độ notification. */
function notificationIcon(type: NotificationType) {
  if (type === "success") return CircleCheck;
  if (type === "warning") return TriangleAlert;
  return CircleAlert;
}

/** Chọn màu icon theo mức độ notification. */
function notificationColor(type: NotificationType): string {
  if (type === "success") return "text-emerald-600";
  if (type === "warning") return "text-amber-600";
  return "text-red-600";
}

/** Chọn màu viền theo mức độ notification. */
function notificationBorder(type: NotificationType): string {
  if (type === "success") return "border-emerald-200";
  if (type === "warning") return "border-amber-200";
  return "border-red-200";
}
