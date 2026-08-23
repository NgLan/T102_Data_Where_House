"use client";

import Image from "next/image";
import { useTranslation } from "react-i18next";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/common/components/ui/tabs";
import { LoginForm } from "./LoginForm";
import { RegisterForm } from "./RegisterForm";

/** Displays login and registration without mounting protected application screens. */
export function AuthScreen() {
  const { t } = useTranslation("auth");
  return (
    <main className="grid min-h-screen place-items-center bg-muted/30 p-4">
      <section className="w-full max-w-md rounded-xl border bg-background p-6 shadow-sm">
        <div className="mb-6 text-center">
          <div className="mx-auto mb-3 flex size-16 items-center justify-center overflow-hidden rounded-2xl bg-white border border-gray-200 p-1 shadow-xs">
            <Image
              src="/AIDWH.png"
              alt="AIDWH Logo"
              width={64}
              height={64}
              className="size-full object-contain scale-110"
              priority
            />
          </div>
          <h1 className="text-xl font-semibold">{t("TXT_TITLE")}</h1>
          <p className="mt-1 text-sm text-muted-foreground">{t("TXT_DESCRIPTION")}</p>
        </div>
        <Tabs defaultValue="login">
          <TabsList className="mb-4 w-full">
            <TabsTrigger value="login">{t("BTN_LOGIN_TAB")}</TabsTrigger>
            <TabsTrigger value="register">{t("BTN_REGISTER_TAB")}</TabsTrigger>
          </TabsList>
          <TabsContent value="login"><LoginForm /></TabsContent>
          <TabsContent value="register"><RegisterForm /></TabsContent>
        </Tabs>
      </section>
    </main>
  );
}
