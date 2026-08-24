"use client";

import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Badge } from "@/common/components/ui/badge";
import { Button } from "@/common/components/ui/button";
import { Play, Pause, Bot, Layout, Database } from "lucide-react";

/** Section hiển thị Video Demo hệ thống với khung phát tương tác và danh sách tính năng chính. */
export function VideoDemoSection() {
  const { t } = useTranslation("landing");
  const [isPlaying, setIsPlaying] = useState(false);

  const togglePlay = () => setIsPlaying((prev) => !prev);

  return (
    <section id="demo" className="relative z-10 py-16 border-t bg-muted/15 backdrop-blur-[1px]">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <Badge variant="outline" className="mb-3">
            {t("TXT_DEMO_BADGE")}
          </Badge>
          <h2 className="text-2xl font-bold sm:text-4xl text-foreground">
            {t("TXT_DEMO_TITLE")}
          </h2>
          <p className="mt-3 text-base text-muted-foreground">
            {t("TXT_DEMO_SUBTITLE")}
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-center">
          {/* Main Video Demo Player Frame */}
          <div className="lg:col-span-2 relative overflow-hidden rounded-2xl border bg-card shadow-lg aspect-video group">
            {isPlaying ? (
              <video
                className="w-full h-full object-cover"
                controls
                autoPlay
                src="/demo/aidwh-demo.mp4"
                poster="/AIDWH.png"
              >
                <track kind="captions" />
                Your browser does not support the video tag.
              </video>
            ) : (
              <div className="relative size-full flex flex-col items-center justify-center bg-gradient-to-br from-slate-900 via-zinc-900 to-stone-900 text-white p-6 text-center">
                <div className="absolute inset-0 bg-black/40 backdrop-blur-[1px]" />
                <div className="relative z-10 space-y-4">
                  <Button
                    size="icon"
                    onClick={togglePlay}
                    aria-label={t("TXT_DEMO_PLAY_OVERLAY")}
                    className="size-16 rounded-full bg-primary text-primary-foreground shadow-xl transition-transform hover:scale-110 cursor-pointer"
                  >
                    <Play className="size-8 fill-current translate-x-0.5" />
                  </Button>
                  <p className="text-sm font-medium text-slate-200">
                    {t("TXT_DEMO_PLAY_OVERLAY")}
                  </p>
                </div>
              </div>
            )}
            {isPlaying && (
              <Button
                size="sm"
                variant="secondary"
                onClick={togglePlay}
                className="absolute top-3 right-3 z-20 gap-1.5 cursor-pointer opacity-90 hover:opacity-100"
              >
                <Pause className="size-4" />
                <span>Pause</span>
              </Button>
            )}
          </div>

          {/* Key Demo Points */}
          <div className="space-y-6">
            <div className="flex gap-4 p-4 rounded-xl border bg-card hover:shadow-md transition-shadow">
              <div className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <Bot className="size-5" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground text-sm">
                  {t("TXT_DEMO_FEATURE_1_TITLE")}
                </h3>
                <p className="text-xs text-muted-foreground mt-1">
                  {t("TXT_DEMO_FEATURE_1_DESC")}
                </p>
              </div>
            </div>

            <div className="flex gap-4 p-4 rounded-xl border bg-card hover:shadow-md transition-shadow">
              <div className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <Layout className="size-5" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground text-sm">
                  {t("TXT_DEMO_FEATURE_2_TITLE")}
                </h3>
                <p className="text-xs text-muted-foreground mt-1">
                  {t("TXT_DEMO_FEATURE_2_DESC")}
                </p>
              </div>
            </div>

            <div className="flex gap-4 p-4 rounded-xl border bg-card hover:shadow-md transition-shadow">
              <div className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <Database className="size-5" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground text-sm">
                  {t("TXT_DEMO_FEATURE_3_TITLE")}
                </h3>
                <p className="text-xs text-muted-foreground mt-1">
                  {t("TXT_DEMO_FEATURE_3_DESC")}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
