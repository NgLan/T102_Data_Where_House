"use client";

import { DatabaseZap } from "lucide-react";
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
          <span className="mx-auto mb-3 grid size-11 place-items-center rounded-xl bg-primary text-primary-foreground">
            <DatabaseZap className="size-5" aria-hidden />
          </span>
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
