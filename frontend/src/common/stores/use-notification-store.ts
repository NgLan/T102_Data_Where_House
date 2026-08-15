import { create } from "zustand";

/** Loại trực quan của một toast trong hệ thống notification. */
export type NotificationType = "error" | "success" | "warning";

/** Nội dung toast đã được dịch trước khi đưa vào hàng đợi. */
export interface AppNotification {
  id: number;
  title: string;
  message: string;
  type: NotificationType;
}

type NotificationInput = Omit<AppNotification, "id">;

interface NotificationState {
  notifications: readonly AppNotification[];
  publish: (notification: NotificationInput) => void;
  dismiss: (id: number) => void;
}

let nextNotificationId = 1;

/** Store toàn cục cho hàng đợi toast tự đóng. */
export const useNotificationStore = create<NotificationState>((set) => ({
  notifications: [],
  publish: (notification) =>
    set((state) => ({
      notifications: [
        ...state.notifications,
        { ...notification, id: nextNotificationId++ },
      ],
    })),
  dismiss: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((item) => item.id !== id),
    })),
}));

/** Phát toast từ code nằm ngoài React như API interceptor. */
export function publishNotification(notification: NotificationInput): void {
  useNotificationStore.getState().publish(notification);
}
