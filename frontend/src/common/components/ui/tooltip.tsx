"use client";

import type { ComponentProps } from "react";
import { Tooltip as TooltipPrimitive } from "radix-ui";
import { cn } from "@/common/lib/utils";

/** Root tooltip dùng chung dựa trên Radix UI đã có trong dự án. */
export function Tooltip(props: ComponentProps<typeof TooltipPrimitive.Root>) {
  return (
    <TooltipPrimitive.Provider delayDuration={300}>
      <TooltipPrimitive.Root {...props} />
    </TooltipPrimitive.Provider>
  );
}

/** Phần tử nhận tương tác hover/focus để mở tooltip. */
export const TooltipTrigger = TooltipPrimitive.Trigger;

/** Nội dung tooltip được render qua portal và có style thống nhất. */
export function TooltipContent({
  className,
  sideOffset = 6,
  ...props
}: ComponentProps<typeof TooltipPrimitive.Content>) {
  return (
    <TooltipPrimitive.Portal>
      <TooltipPrimitive.Content
        sideOffset={sideOffset}
        className={cn(
          "z-50 rounded-md bg-slate-900 px-2.5 py-1.5 text-xs text-white shadow-md animate-in fade-in zoom-in-95",
          className,
        )}
        {...props}
      />
    </TooltipPrimitive.Portal>
  );
}
