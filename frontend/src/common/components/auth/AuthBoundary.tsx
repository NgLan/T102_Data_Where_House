"use client";

import type { ReactNode } from "react";
import { usePathname } from "next/navigation";
import { useTranslation } from "react-i18next";
import { isApiError, resolveApiErrorMessage } from "@/api";
import { Button } from "@/common/components/ui/button";
import { Skeleton } from "@/common/components/ui/skeleton";
import { useCurrentActorQuery } from "@/common/projects/project-queries";
import { AuthScreen } from "@/features/auth/components/AuthScreen";
import { LandingScreen } from "@/features/landing";

interface AuthBoundaryProps {
  children: ReactNode;
}

/** Mounts business screens only after the cookie-backed user is authenticated. */
export function AuthBoundary({ children }: AuthBoundaryProps) {
  const { t } = useTranslation("auth");
  const pathname = usePathname();
  const actorQuery = useCurrentActorQuery();

  if (actorQuery.isPending && !actorQuery.data && !actorQuery.error) return <AuthLoading />;

  if (isUnauthenticated(actorQuery.error)) {
    if (pathname === "/auth" || pathname === "/login") {
      return <AuthScreen />;
    }
    return <LandingScreen />;
  }
  if (actorQuery.isError) {
    const message = isApiError(actorQuery.error)
      ? resolveApiErrorMessage(actorQuery.error)
      : t("MSG_AUTH_UNAVAILABLE");
    return (
      <main className="grid min-h-screen place-items-center p-4">
        <div className="max-w-md text-center">
          <p className="mb-4 text-sm text-destructive" role="alert">{message}</p>
          <Button onClick={() => actorQuery.refetch()}>{t("BTN_RETRY")}</Button>
        </div>
      </main>
    );
  }
  return children;
}

function isUnauthenticated(error: unknown): boolean {
  return isApiError(error) && error.kind === "authentication";
}

function AuthLoading() {
  return (
    <main className="grid min-h-screen place-items-center" aria-busy="true">
      <div className="w-full max-w-md space-y-3 p-6">
        <Skeleton className="mx-auto size-11 rounded-xl" />
        <Skeleton className="mx-auto h-6 w-48" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
      </div>
    </main>
  );
}
