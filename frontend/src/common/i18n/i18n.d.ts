import { resources, defaultNS } from './i18n';

/**
 * Định nghĩa Type mở rộng cho react-i18next để hỗ trợ Autocomplete & Type Safety cho translation keys.
 */
declare module 'i18next' {
  interface CustomTypeOptions {
    defaultNS: typeof defaultNS;
    resources: (typeof resources)['vi'];
  }
}
