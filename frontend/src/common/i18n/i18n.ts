import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Import tài nguyên ngôn ngữ Tiếng Việt
import commonVi from '../locales/vi/common.json';
import notificationsVi from '../locales/vi/notifications.json';
import errorsVi from '../locales/vi/errors.json';
import projectInitVi from '../locales/vi/projectInit.json';

// Import tài nguyên ngôn ngữ Tiếng Anh
import commonEn from '../locales/en/common.json';
import notificationsEn from '../locales/en/notifications.json';
import errorsEn from '../locales/en/errors.json';
import projectInitEn from '../locales/en/projectInit.json';

/**
 * Cấu hình tập trung các nguồn tài nguyên đa ngôn ngữ (Resources).
 */
export const defaultNS = 'common';

export const resources = {
  vi: {
    common: commonVi,
    notifications: notificationsVi,
    errors: errorsVi,
    projectInit: projectInitVi,
  },
  en: {
    common: commonEn,
    notifications: notificationsEn,
    errors: errorsEn,
    projectInit: projectInitEn,
  },
} as const;

/**
 * Khởi tạo cấu hình i18next cho ứng dụng Next.js App Router.
 * Thiết lập lng: 'vi' mặc định để đảm bảo đồng bộ HTML 100% giữa Server (SSR) và Initial Client Render,
 * giải quyết hoàn toàn rủi ro Hydration Mismatch.
 */
if (!i18n.isInitialized) {
  i18n
    .use(initReactI18next)
    .init({
      resources,
      lng: 'vi', // Đặt ngôn ngữ khởi tạo nhất quán với Server HTML
      fallbackLng: 'vi',
      defaultNS,
      interpolation: {
        escapeValue: false, // React đã tự động chống XSS
      },
    });
}

export default i18n;
