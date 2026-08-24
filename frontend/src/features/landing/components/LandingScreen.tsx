"use client";

import { useTranslation } from "react-i18next";
import { LandingHeader } from "./LandingHeader";
import { HeroSection } from "./HeroSection";
import { FeaturesSection } from "./FeaturesSection";
import { VideoDemoSection } from "./VideoDemoSection";
import { DocsSection } from "./DocsSection";
import { LandingFooter } from "./LandingFooter";
import { ParticlesBackground } from "./ParticlesBackground";
import { ScrollToTop } from "@/common/components/ui/ScrollToTop";

/** Screen chính cho Landing Page giới thiệu trang web.
 * Bao gồm các section: Hero, Features, Video Demo và Docs Placeholder. Nút Đăng nhập chuyển sang trang /auth.
 */
export function LandingScreen() {
  const { i18n } = useTranslation();
  const scrollToTopLabel = i18n.resolvedLanguage === "vi" ? "Lên đầu trang" : "Back to top";

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans">
      <LandingHeader />
      <main className="relative flex-1 overflow-hidden">
        <ParticlesBackground />
        <HeroSection />
        <FeaturesSection />
        <VideoDemoSection />
        <DocsSection />
      </main>
      <LandingFooter />
      <ScrollToTop tooltip={scrollToTopLabel} />
    </div>
  );
}
