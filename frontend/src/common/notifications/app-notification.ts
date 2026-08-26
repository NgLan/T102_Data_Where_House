import { toast } from "sonner";

interface AppNotification {
  title: string;
  message: string;
}

/** Hiển thị thông báo thành công qua registry toast dùng chung. */
export function notifyAppSuccess(notification: AppNotification): void {
  toast.success(notification.title, { description: notification.message });
}

/** Hiển thị thông báo lỗi qua registry toast dùng chung. */
export function notifyAppError(notification: AppNotification): void {
  toast.error(notification.title, { description: notification.message });
}

/** Hiển thị cảnh báo qua registry toast dùng chung. */
export function notifyAppWarning(notification: AppNotification): void {
  toast.warning(notification.title, { description: notification.message });
}

/** Hiển thị thông tin qua registry toast dùng chung. */
export function notifyAppInfo(notification: AppNotification): void {
  toast.info(notification.title, { description: notification.message });
}

