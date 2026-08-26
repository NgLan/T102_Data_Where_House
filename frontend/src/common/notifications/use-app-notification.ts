'use client';

import { useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import {
  notifyAppError,
  notifyAppInfo,
  notifyAppSuccess,
  notifyAppWarning,
} from './app-notification';
import { resolveErrorMessage } from '@/api/errors/resolve-error-message';
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
 * @returns Các hàm tạo thông báo thành công, lỗi, cảnh báo và thông tin.
 */
export function useAppNotification() {
  const { t: tNotify } = useTranslation('notifications');
  const { t: tErrors } = useTranslation('errors');

  const getErrorMessage = useCallback((
    errorCode?: ErrorCodeKey,
    fallbackKey: ErrorCodeKey = 'UNKNOWN_ERROR',
  ): string => {
    const fallback = tErrors(fallbackKey, { defaultValue: tErrors('UNKNOWN_ERROR') });
    const translated = errorCode ? tErrors(errorCode, { defaultValue: '' }) : '';
    return resolveErrorMessage(translated, fallback);
  }, [tErrors]);

  const notifySuccess = useCallback((key: NotificationKey, options?: NotificationOptions) => {
    notifyAppSuccess({
      title: tNotify('TXT_SUCCESS_TITLE'),
      message: tNotify(key, options?.params),
    });
  }, [tNotify]);

  const notifyError = useCallback((
    errorCode?: ErrorCodeKey,
    fallbackKey: ErrorCodeKey = 'UNKNOWN_ERROR'
  ) => {
    notifyAppError({
      title: tNotify('TXT_ERROR_TITLE'),
      message: getErrorMessage(errorCode, fallbackKey),
    });
  }, [getErrorMessage, tNotify]);

  const notifyWarning = useCallback((key: NotificationKey, options?: NotificationOptions) => {
    notifyAppWarning({
      title: tNotify('TXT_WARNING_TITLE'),
      message: tNotify(key, options?.params),
    });
  }, [tNotify]);

  const notifyInfo = useCallback((key: NotificationKey, options?: NotificationOptions) => {
    notifyAppInfo({
      title: tNotify('TXT_INFO_TITLE'),
      message: tNotify(key, options?.params),
    });
  }, [tNotify]);

  return { getErrorMessage, notifySuccess, notifyError, notifyWarning, notifyInfo };
}
