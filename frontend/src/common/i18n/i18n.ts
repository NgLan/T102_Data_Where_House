import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import commonVi from './locales/vi/common.json';
import notificationsVi from './locales/vi/notifications.json';
import errorsVi from './locales/vi/errors.json';
import projectInitVi from './locales/vi/project-init.json';
import modelingDashboardVi from './locales/vi/modeling-dashboard.json';
import sandboxDeploymentVi from './locales/vi/sandbox-deployment.json';

import commonEn from './locales/en/common.json';
import notificationsEn from './locales/en/notifications.json';
import errorsEn from './locales/en/errors.json';
import projectInitEn from './locales/en/project-init.json';
import modelingDashboardEn from './locales/en/modeling-dashboard.json';
import sandboxDeploymentEn from './locales/en/sandbox-deployment.json';

/** Namespace mặc định cho nội dung dùng chung. */
export const defaultNS = 'common';

/** Tài nguyên VI/EN đã đăng ký theo namespace feature. */
export const resources = {
  vi: {
    common: commonVi,
    notifications: notificationsVi,
    errors: errorsVi,
    'project-init': projectInitVi,
    'modeling-dashboard': modelingDashboardVi,
    'sandbox-deployment': sandboxDeploymentVi,
  },
  en: {
    common: commonEn,
    notifications: notificationsEn,
    errors: errorsEn,
    'project-init': projectInitEn,
    'modeling-dashboard': modelingDashboardEn,
    'sandbox-deployment': sandboxDeploymentEn,
  },
} as const;

if (!i18n.isInitialized) {
  i18n
    .use(initReactI18next)
    .init({
      resources,
      lng: 'vi',
      fallbackLng: 'vi',
      defaultNS,
      interpolation: {
        escapeValue: false,
      },
    });
}

export default i18n;
