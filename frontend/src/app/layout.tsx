import type { Metadata } from 'next';
import type { ReactNode } from 'react';
import { AppProviders } from '@/common/providers/AppProviders';
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
    <html lang="vi" className="font-sans" suppressHydrationWarning>
      <body className="antialiased">
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}

