"use client";

/** Render các hiệu ứng quét laser, sóng quét radar và ánh sáng trung tâm. */
export function TechScanEffects() {
  return (
    <>
      {/* Ánh sáng đỏ khuếch tán tại trung tâm phía sau form */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[500px] w-[500px] rounded-full bg-red-500/10 dark:bg-red-600/15 blur-[120px]" />

      {/* Tia laser quét dọc ma trận */}
      <div className="absolute inset-x-0 h-32 bg-gradient-to-b from-transparent via-red-500/15 dark:via-red-500/20 to-transparent blur-sm animate-[scan-beam_8s_linear_infinite]" />

      {/* Sóng quét radar lan tỏa từ trung tâm */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 size-[650px] rounded-full border border-red-500/20 dark:border-red-500/30 animate-[radar-ripple_6s_ease-out_infinite]" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 size-[650px] rounded-full border border-orange-500/15 dark:border-orange-500/20 animate-[radar-ripple_6s_ease-out_infinite_3s]" />
    </>
  );
}
