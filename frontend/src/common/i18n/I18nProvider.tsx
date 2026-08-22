'use client';

import React, { ReactNode, useEffect } from 'react';
import { I18nextProvider } from 'react-i18next';
import i18n from './i18n';

/**
 * Interface cho Props của I18nProvider Component.
 */
interface I18nProviderProps {
  /** Các component con bên trong ứng dụng */
  children: ReactNode;
}

/**
 * Component Provider bọc i18n context cấp cao nhất cho ứng dụng Client-side.
 * Giúp đồng bộ hóa ngôn ngữ người dùng đã chọn từ localStorage SAU KHI quá trình Hydration của Next.js hoàn tất,
 * giúp loại bỏ 100% rủi ro Hydration Mismatch hoặc UI Flickering.
 *
 * @param props Props chứa danh sách children components
 */
export const I18nProvider: React.FC<I18nProviderProps> = ({ children }) => {
  useEffect(() => {
    // Kích hoạt đồng bộ ngôn ngữ từ localStorage sau khi Client Hydration kết thúc
    if (typeof window !== 'undefined') {
      const savedLang = localStorage.getItem('i18nextLng');
      if (
        savedLang &&
        (savedLang === 'vi' || savedLang === 'en') &&
        savedLang !== i18n.language
      ) {
        i18n.changeLanguage(savedLang);
      }
    }
    const handleLanguageChanged = (language: string) => {
      const normalizedLanguage = language.startsWith('en') ? 'en' : 'vi';
      document.documentElement.lang = normalizedLanguage;
      localStorage.setItem('i18nextLng', normalizedLanguage);
    };
    i18n.on('languageChanged', handleLanguageChanged);
    handleLanguageChanged(i18n.resolvedLanguage ?? i18n.language);
    return () => { i18n.off('languageChanged', handleLanguageChanged); };
  }, []);

  return <I18nextProvider i18n={i18n}>{children}</I18nextProvider>;
};

export default I18nProvider;
