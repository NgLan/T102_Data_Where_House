"use client";

import { useMemo, useSyncExternalStore } from "react";
import Particles, { ParticlesProvider } from "@tsparticles/react";
import type { Engine, ISourceOptions } from "@tsparticles/engine";
import { loadSlim } from "@tsparticles/slim";
import { useTheme } from "next-themes";

const initParticles = async (engine: Engine): Promise<void> => {
  await loadSlim(engine);
};

const subscribeToClient = () => () => undefined;

/** Nền hiệu ứng hạt tương tác chuột sử dụng thư viện @tsparticles/react & @tsparticles/slim.
 * Tự động chuyển đổi màu tương phản rõ nét theo Dark/Light theme và kết nối tia sáng khi rê chuột.
 */
export function ParticlesBackground() {
  const { resolvedTheme } = useTheme();
  const mounted = useSyncExternalStore(
    subscribeToClient,
    () => process.env.NODE_ENV !== "test",
    () => false,
  );

  const isDark = resolvedTheme === "dark";

  const options: ISourceOptions = useMemo(
    () => ({
      fullScreen: { enable: false },
      fpsLimit: 60,
      interactivity: {
        detectsOn: "window",
        events: {
          onHover: {
            enable: true,
            mode: "grab",
          },
          resize: { enable: true },
        },
        modes: {
          grab: {
            distance: 200,
            links: {
              opacity: 0.9,
              color: isDark ? "#f87171" : "#dc2626",
            },
          },
        },
      },
      particles: {
        color: {
          value: isDark ? ["#ffffff", "#fca5a5", "#ffffff"] : ["#09090b", "#18181b", "#000000"],
        },
        links: {
          color: isDark ? "#ef4444" : "#dc2626",
          distance: 140,
          enable: true,
          opacity: isDark ? 0.35 : 0.45,
          width: 1.2,
          triangles: {
            enable: false,
          },
        },
        move: {
          enable: true,
          speed: 1.2,
          direction: "none",
          outModes: {
            default: "bounce",
          },
        },
        number: {
          density: {
            enable: true,
            width: 1100,
            height: 800,
          },
          value: 80,
        },
        opacity: {
          value: 1,
        },
        shape: {
          type: ["circle", "triangle"],
        },
        size: {
          value: isDark ? { min: 3, max: 5.5 } : { min: 4, max: 6.5 },
        },
      },
      detectRetina: true,
    }),
    [isDark]
  );

  if (!mounted) return null;

  const currentThemeKey = isDark ? "dark" : "light";

  return (
    <div className="pointer-events-none absolute inset-0 z-0 overflow-hidden" aria-hidden="true">
      <ParticlesProvider init={initParticles}>
        <Particles
          key={currentThemeKey}
          id={`tsparticles-landing-${currentThemeKey}`}
          options={options}
          className="size-full"
        />
      </ParticlesProvider>
    </div>
  );
}
