"use client"

import { useTheme } from "next-themes"
import { Toaster as Sonner, type ToasterProps } from "sonner"
import { CircleCheckIcon, InfoIcon, TriangleAlertIcon, OctagonXIcon, Loader2Icon } from "lucide-react"

const Toaster = ({ position = "top-right", ...props }: ToasterProps) => {
  const { theme = "system" } = useTheme()

  return (
    <Sonner
      theme={theme as ToasterProps["theme"]}
      position={position}
      className="toaster group"
      richColors
      icons={{
        success: (
          <CircleCheckIcon className="size-4 text-emerald-600 dark:text-emerald-400" />
        ),
        info: (
          <InfoIcon className="size-4 text-blue-600 dark:text-blue-400" />
        ),
        warning: (
          <TriangleAlertIcon className="size-4 text-amber-600 dark:text-amber-400" />
        ),
        error: (
          <OctagonXIcon className="size-4 text-rose-600 dark:text-rose-400" />
        ),
        loading: (
          <Loader2Icon className="size-4 animate-spin text-muted-foreground" />
        ),
      }}
      style={
        {
          "--normal-bg": "var(--popover)",
          "--normal-text": "var(--popover-foreground)",
          "--normal-border": "var(--border)",
          "--border-radius": "var(--radius)",
        } as React.CSSProperties
      }
      toastOptions={{
        classNames: {
          toast: "cn-toast font-sans border shadow-md",
          title: "font-semibold text-sm",
          description: "text-xs opacity-90",
          success:
            "!bg-emerald-50 !text-emerald-950 !border-emerald-200 dark:!bg-emerald-950/80 dark:!text-emerald-100 dark:!border-emerald-800",
          error:
            "!bg-rose-50 !text-rose-950 !border-rose-200 dark:!bg-rose-950/80 dark:!text-rose-100 dark:!border-rose-800",
          warning:
            "!bg-amber-50 !text-amber-950 !border-amber-200 dark:!bg-amber-950/80 dark:!text-amber-100 dark:!border-amber-800",
          info:
            "!bg-blue-50 !text-blue-950 !border-blue-200 dark:!bg-blue-950/80 dark:!text-blue-100 dark:!border-blue-800",
        },
      }}
      {...props}
    />
  )
}

export { Toaster }
