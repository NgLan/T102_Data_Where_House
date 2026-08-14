'use client';

import React from 'react';
import { useTranslation } from 'react-i18next';
import { Globe } from 'lucide-react';

/**
 * Component nút bấm chuyển đổi ngôn ngữ (Tiếng Việt <-> English).
 * Thường được nhúng trên Header hoặc Thanh công cụ của hệ thống.
 */
export const LanguageSwitcher: React.FC = () => {
  const { i18n, t } = useTranslation('common');

  /** Ngôn ngữ hiện tại */
  const currentLanguage = i18n.language || 'vi';

  /**
   * Thao tác chuyển đổi ngôn ngữ giữa 'vi' và 'en' và lưu vào localStorage
   */
  const handleToggleLanguage = () => {
    const nextLang = currentLanguage.startsWith('vi') ? 'en' : 'vi';
    i18n.changeLanguage(nextLang);
    if (typeof window !== 'undefined') {
      localStorage.setItem('i18nextLng', nextLang);
    }
  };

  return (
    <button
      onClick={handleToggleLanguage}
      type="button"
      className="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 hover:text-slate-900 transition-colors shadow-sm focus:outline-none focus:ring-2 focus:ring-slate-300"
      title={t('language.switch_language')}
      aria-label={t('language.switch_language')}
    >
      <Globe className="w-4 h-4 text-slate-500" />
      <span className="uppercase font-semibold text-xs">
        {currentLanguage.startsWith('vi') ? 'VI' : 'EN'}
      </span>
      <span className="hidden sm:inline text-xs text-slate-500">
        ({currentLanguage.startsWith('vi') ? t('language.vietnamese') : t('language.english')})
      </span>
    </button>
  );
};

export default LanguageSwitcher;
