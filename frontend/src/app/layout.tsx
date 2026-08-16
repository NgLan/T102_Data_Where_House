import type { Metadata } from 'next';
import type { ReactNode } from 'react';
import { I18nProvider } from '@/common/i18n/I18nProvider';
import { NotificationCenter } from '@/common/components/ui/notification-center';
import commonVi from '@/common/i18n/locales/vi/common.json';
import './globals.css';

export const metadata: Metadata = {
  title: commonVi.TXT_APP_NAME,
  description: commonVi.TXT_APP_DESCRIPTION,
};

/** Cấu hình document root, font và provider dùng chung của App Router.
 * @param props Nội dung route hiện hành.
 * @returns Root HTML layout của ứng dụng.
 */
export default function RootLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="vi" className="font-sans">
      <body className="antialiased">
        <I18nProvider>
          {children}
          <NotificationCenter />
        </I18nProvider>
      </body>
    </html>
  );
}

