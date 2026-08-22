"use client";

import { useState, type ReactNode } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "next-themes";
import { TooltipProvider } from "@/common/components/ui/tooltip";
import { Toaster } from "@/common/components/ui/sonner";
import { I18nProvider } from "@/common/i18n/I18nProvider";

interface AppProvidersProps {
  children: ReactNode;
}

/** Ghép các provider client dùng chung của ứng dụng.
 * @param props Nội dung App Router cần dùng theme, query, tooltip và i18n.
 * @returns Cây provider có QueryClient ổn định trong suốt vòng đời browser.
 */
export function AppProviders({ children }: AppProvidersProps) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: { queries: { staleTime: 30_000, retry: 1 } },
  }));
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <I18nProvider>
        <QueryClientProvider client={queryClient}>
          <TooltipProvider>{children}</TooltipProvider>
          <Toaster />
        </QueryClientProvider>
      </I18nProvider>
    </ThemeProvider>
  );
}
