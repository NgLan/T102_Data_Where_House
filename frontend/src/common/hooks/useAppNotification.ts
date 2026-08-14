'use client';

import { useTranslation } from 'react-i18next';
import notificationsVi from '../locales/vi/notifications.json';
import errorsVi from '../locales/vi/errors.json';

/**
 * Type helper trích xuất tất cả các chìa khóa con (leaf keys) từ JSON object theo định dạng dot-notation.
 * Ví dụ: 'project_init.upload_success' | 'general.action_completed'
 */
type LeafKeys<T> = T extends object
  ? {
      [K in keyof T & string]: T[K] extends object
        ? `${K}.${LeafKeys<T[K]>}`
        : `${K}`;
    }[keyof T & string]
  : never;

/** Kiểu dữ liệu chìa khóa thông báo thuộc notifications.json */
export type NotificationKey = LeafKeys<typeof notificationsVi>;

/** Kiểu dữ liệu mã lỗi thuộc errors.json (hoặc chuỗi mã lỗi động từ Backend API) */
export type ErrorCodeKey = keyof typeof errorsVi | (string & {});

/**
 * Kiểu dữ liệu cho tùy chọn phát thông báo.
 */
export interface NotificationOptions {
  /** Tham số nội hàm để thay thế trong chuỗi translation (ví dụ: {{count}}) */
  params?: Record<string, string | number>;
  /** Tiêu đề tùy chỉnh nếu không muốn dùng tiêu đề mặc định */
  customTitle?: string;
}

/**
 * Custom hook quản lý hiển thị thông báo và báo lỗi chuẩn hóa qua i18n keys.
 * Đảm bảo 100% Type Safety, tự động gợi ý chìa khóa dịch trong IDE mà không cần dùng 'as any' hay 'as never'.
 */
export function useAppNotification() {
  const { t: tNotify } = useTranslation('notifications');
  const { t: tErrors } = useTranslation('errors');

  /**
   * Hiển thị thông báo thành công.
   *
   * @param notificationKey Key thuộc namespace 'notifications' (ví dụ: 'project_init.upload_success')
   * @param options Tùy chọn tham số truyền vào chuỗi dịch
   */
  const notifySuccess = (
    notificationKey: NotificationKey,
    options?: NotificationOptions
  ) => {
    const title = options?.customTitle || tNotify('titles.success');
    const message = tNotify(notificationKey, options?.params);

    console.log(`[SUCCESS] ${title}: ${message}`);
    return { title, message, type: 'success' as const };
  };

  /**
   * Hiển thị thông báo lỗi dựa trên Backend ErrorCode hoặc Error Key.
   *
   * @param errorCode Mã lỗi từ API backend (ví dụ: 'INVALID_INPUT_SCHEMA') hoặc error key
   * @param fallbackKey Key dự phòng nếu không tìm thấy errorCode trong errors.json
   */
  const notifyError = (
    errorCode?: ErrorCodeKey,
    fallbackKey: ErrorCodeKey = 'UNKNOWN_ERROR'
  ) => {
    const title = tNotify('titles.error');

    // Tìm dịch mã lỗi từ Backend ErrorCode trước
    let message = errorCode ? tErrors(errorCode, { defaultValue: '' }) : '';

    // Nếu không có dịch mã lỗi cụ thể, sử dụng fallback key
    if (!message) {
      message = tErrors(fallbackKey, { defaultValue: tErrors('UNKNOWN_ERROR') });
    }

    console.error(`[ERROR] ${title}: ${message}`);
    return { title, message, type: 'error' as const };
  };

  /**
   * Hiển thị cảnh báo.
   *
   * @param notificationKey Key thông báo cảnh báo
   * @param options Tham số truyền vào
   */
  const notifyWarning = (
    notificationKey: NotificationKey,
    options?: NotificationOptions
  ) => {
    const title = options?.customTitle || tNotify('titles.warning');
    const message = tNotify(notificationKey, options?.params);

    console.warn(`[WARNING] ${title}: ${message}`);
    return { title, message, type: 'warning' as const };
  };

  return {
    notifySuccess,
    notifyError,
    notifyWarning,
  };
}
