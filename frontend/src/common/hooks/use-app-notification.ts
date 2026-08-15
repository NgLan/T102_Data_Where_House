'use client';

import { useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { publishNotification } from '@/common/stores/use-notification-store';
import errorsVi from '../i18n/locales/vi/errors.json';
import notificationsVi from '../i18n/locales/vi/notifications.json';

export type NotificationKey = keyof typeof notificationsVi;
export type ErrorCodeKey = keyof typeof errorsVi | (string & Record<never, never>);

export interface NotificationOptions {
  params?: Record<string, string | number>;
}

/**
 * Cung cấp các hàm tạo thông báo đã chuẩn hóa và dịch theo locale hiện tại.
 *
 * @returns Các hàm tạo thông báo thành công, lỗi và cảnh báo.
 */
export function useAppNotification() {
  const { t: tNotify } = useTranslation('notifications');
  const { t: tErrors } = useTranslation('errors');

  const getErrorMessage = useCallback((
    errorCode?: ErrorCodeKey,
    fallbackKey: ErrorCodeKey = 'UNKNOWN_ERROR',
  ): string => {
    const message = errorCode ? tErrors(errorCode, { defaultValue: '' }) : '';
    return message || tErrors(fallbackKey, { defaultValue: tErrors('UNKNOWN_ERROR') });
  }, [tErrors]);

  const notifySuccess = useCallback((key: NotificationKey, options?: NotificationOptions) => {
    publishNotification({
      title: tNotify('TXT_SUCCESS_TITLE'),
      message: tNotify(key, options?.params),
      type: 'success',
    });
  }, [tNotify]);

  const notifyError = useCallback((
    errorCode?: ErrorCodeKey,
    fallbackKey: ErrorCodeKey = 'UNKNOWN_ERROR'
  ) => {
    publishNotification({
      title: tNotify('TXT_ERROR_TITLE'),
      message: getErrorMessage(errorCode, fallbackKey),
      type: 'error',
    });
  }, [getErrorMessage, tNotify]);

  const notifyWarning = useCallback((key: NotificationKey, options?: NotificationOptions) => {
    publishNotification({
      title: tNotify('TXT_WARNING_TITLE'),
      message: tNotify(key, options?.params),
      type: 'warning',
    });
  }, [tNotify]);

  return { getErrorMessage, notifySuccess, notifyError, notifyWarning };
}
