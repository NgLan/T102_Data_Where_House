"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { useTranslation } from "react-i18next";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/common/components/ui/tabs";
import { ArrowLeft } from "lucide-react";
import { TechGridBackground } from "./tech-grid";
import { LoginForm } from "./LoginForm";
import { RegisterForm } from "./RegisterForm";

/** Displays login and registration with interactive dynamic background and glassmorphism card. */
export function AuthScreen() {
  const { t } = useTranslation("auth");
  const [activeTab, setActiveTab] = useState<string>("login");
  const [prefilledUsername, setPrefilledUsername] = useState<string>("");

  const handleRegisterSuccess = (registeredUsername: string) => {
    setPrefilledUsername(registeredUsername);
    setActiveTab("login");
  };

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-background p-4 sm:p-6 font-sans">
      <TechGridBackground />

      {/* Main Glassmorphism Auth Card */}
      <section className="relative z-10 w-full max-w-md rounded-2xl border border-border/80 bg-background/80 dark:bg-card/80 p-5 sm:p-6 shadow-2xl backdrop-blur-xl transition-all">
        <div className="mb-2.5">
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 rounded-md px-1.5 py-0.5 text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-muted/60 transition-colors"
          >
            <ArrowLeft className="size-3.5" />
            <span>{t("BTN_BACK_TO_HOME")}</span>
          </Link>
        </div>
        <div className="mb-4 text-center">
          <div className="mx-auto mb-2 flex size-12 items-center justify-center overflow-hidden rounded-xl bg-white border border-gray-200/80 p-1 shadow-xs">
            <Image
              src="/AIDWH.png"
              alt="AIDWH Logo"
              width={48}
              height={48}
              className="size-full object-contain scale-105"
              priority
            />
          </div>
          <h1 className="text-xl font-bold tracking-tight">{t("TXT_TITLE")}</h1>
          <p className="mt-0.5 text-xs text-muted-foreground">{t("TXT_DESCRIPTION")}</p>
        </div>
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="mb-3.5 h-10 w-full p-1 bg-muted/70 rounded-xl">
            <TabsTrigger
              value="login"
              className="flex-1 h-8 text-xs font-medium transition-all data-[state=active]:shadow-xs data-[state=active]:font-semibold"
            >
              {t("BTN_LOGIN_TAB")}
            </TabsTrigger>
            <TabsTrigger
              value="register"
              className="flex-1 h-8 text-xs font-medium transition-all data-[state=active]:shadow-xs data-[state=active]:font-semibold"
            >
              {t("BTN_REGISTER_TAB")}
            </TabsTrigger>
          </TabsList>
          <TabsContent value="login" className="mt-0 focus-visible:outline-none">
            <LoginForm defaultIdentifier={prefilledUsername} />
          </TabsContent>
          <TabsContent value="register" className="mt-0 focus-visible:outline-none">
            <RegisterForm onRegisterSuccess={handleRegisterSuccess} />
          </TabsContent>
        </Tabs>
      </section>
    </main>
  );
}
