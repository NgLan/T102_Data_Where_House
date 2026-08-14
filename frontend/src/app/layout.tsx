import type { Metadata } from 'next';
import { I18nProvider } from '@/common/i18n/I18nProvider';
import './globals.css';

export const metadata: Metadata = {
  title: 'Data Model AI Agent - Enterprise Prototype',
  description: 'Công cụ phân tích và tự động dựng mô hình dữ liệu Data Warehouse bằng AI Agent',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi">
      <body className="antialiased">
        <I18nProvider>{children}</I18nProvider>
      </body>
    </html>
  );
}

