"use client";

import { TechGridSvg } from "./TechGridSvg";
import { TechDataNodes } from "./TechDataNodes";
import { TechScanEffects } from "./TechScanEffects";

/** Nền hiệu ứng Tech Data Grid + Radial Beam + Multi-spectrum Glowing Data Nodes (Lựa chọn 3).
 * Điều phối các layer SVG Grid, hiệu ứng quét laser, radar và mạng lưới điểm nút phát sáng.
 */
export function TechGridBackground() {
  return (
    <div className="pointer-events-none absolute inset-0 z-0 overflow-hidden" aria-hidden="true">
      <div className="absolute inset-0 bg-slate-50/70 dark:bg-zinc-950/95" />
      <TechGridSvg />
      <TechScanEffects />
      <TechDataNodes />
      <TechGridStyles />
    </div>
  );
}

function TechGridStyles() {
  return (
    <style jsx>{`
      @keyframes scan-beam {
        0% {
          top: -15%;
          opacity: 0;
        }
        20% {
          opacity: 1;
        }
        80% {
          opacity: 1;
        }
        100% {
          top: 110%;
          opacity: 0;
        }
      }
      @keyframes radar-ripple {
        0% {
          transform: translate(-50%, -50%) scale(0.2);
          opacity: 0.8;
        }
        70% {
          opacity: 0.4;
        }
        100% {
          transform: translate(-50%, -50%) scale(1.4);
          opacity: 0;
        }
      }
      @keyframes node-twinkle {
        0%,
        100% {
          opacity: 0.2;
          transform: scale(0.7);
        }
        50% {
          opacity: 1;
          transform: scale(1.3);
        }
      }
      @keyframes node-pulse {
        0%,
        100% {
          opacity: 0.4;
          transform: scale(0.85);
        }
        50% {
          opacity: 1;
          transform: scale(1.15);
        }
      }
      @keyframes node-pulse-deep {
        0%,
        100% {
          opacity: 0.3;
          transform: scale(0.8);
        }
        50% {
          opacity: 1;
          transform: scale(1.35);
        }
      }
      @keyframes node-ring {
        0% {
          transform: translate(-50%, -50%) scale(0.5);
          opacity: 1;
        }
        100% {
          transform: translate(-50%, -50%) scale(2.2);
          opacity: 0;
        }
      }
    `}</style>
  );
}
