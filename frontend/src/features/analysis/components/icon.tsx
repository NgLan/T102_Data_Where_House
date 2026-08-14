import { cn } from "@/common/utils/cn";

export type IconName =
  | "alert"
  | "brain"
  | "check"
  | "chevron"
  | "close"
  | "copy"
  | "code"
  | "database"
  | "download"
  | "grid"
  | "key"
  | "layers"
  | "menu"
  | "network"
  | "refresh"
  | "save"
  | "search"
  | "sparkles"
  | "table";

interface IconProps {
  name: IconName;
  className?: string;
}

/** Hiển thị icon nét đồng nhất cho giao diện workspace. */
export function Icon({ name, className }: IconProps) {
  const commonProps = {
    className: cn("size-5 shrink-0", className),
    fill: "none",
    stroke: "currentColor",
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    strokeWidth: 1.8,
    viewBox: "0 0 24 24",
    "aria-hidden": true,
  };

  switch (name) {
    case "alert":
      return <svg {...commonProps}><path d="M10.3 3.8 2 18a2 2 0 0 0 1.7 3h16.6a2 2 0 0 0 1.7-3L13.7 3.8a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4m0 4h.01"/></svg>;
    case "brain":
      return <svg {...commonProps}><path d="M9.5 4.5A3 3 0 0 0 4 6a3 3 0 0 0 .5 5.5A3.5 3.5 0 0 0 9 17v2a2 2 0 0 0 4 0V5a3 3 0 0 0-3.5-.5Z"/><path d="M14.5 4.5A3 3 0 0 1 20 6a3 3 0 0 1-.5 5.5A3.5 3.5 0 0 1 15 17m-6-8a2 2 0 0 1-2 2m8-2a2 2 0 0 0 2 2m-8 4a2 2 0 0 0 2-2m4 2a2 2 0 0 1-2-2"/></svg>;
    case "check":
      return <svg {...commonProps}><path d="m5 12 4 4L19 6"/></svg>;
    case "chevron":
      return <svg {...commonProps}><path d="m9 18 6-6-6-6"/></svg>;
    case "close":
      return <svg {...commonProps}><path d="m6 6 12 12M18 6 6 18"/></svg>;
    case "copy":
      return <svg {...commonProps}><rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/></svg>;
    case "code":
      return <svg {...commonProps}><path d="m8 9-3 3 3 3m8-6 3 3-3 3m-2-9-4 12"/></svg>;
    case "database":
      return <svg {...commonProps}><ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/></svg>;
    case "download":
      return <svg {...commonProps}><path d="M12 3v12m-4-4 4 4 4-4M5 21h14"/></svg>;
    case "grid":
      return <svg {...commonProps}><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>;
    case "key":
      return <svg {...commonProps}><circle cx="8" cy="15" r="4"/><path d="m11 12 8-8m-3 3 2 2m-5 1 2 2"/></svg>;
    case "layers":
      return <svg {...commonProps}><path d="m12 2 9 5-9 5-9-5 9-5Z"/><path d="m3 12 9 5 9-5M3 17l9 5 9-5"/></svg>;
    case "menu":
      return <svg {...commonProps}><path d="M4 6h16M4 12h16M4 18h16"/></svg>;
    case "network":
      return <svg {...commonProps}><rect x="9" y="2" width="6" height="5" rx="1"/><rect x="2" y="17" width="6" height="5" rx="1"/><rect x="16" y="17" width="6" height="5" rx="1"/><path d="M12 7v4m-7 6v-2a4 4 0 0 1 4-4h6a4 4 0 0 1 4 4v2"/></svg>;
    case "refresh":
      return <svg {...commonProps}><path d="M20 6v5h-5M4 18v-5h5"/><path d="M18 9a7 7 0 0 0-12-3L4 8m2 7a7 7 0 0 0 12 3l2-2"/></svg>;
    case "save":
      return <svg {...commonProps}><path d="M5 3h12l3 3v15H4V4a1 1 0 0 1 1-1Z"/><path d="M8 3v6h8V3m-8 18v-7h8v7"/></svg>;
    case "search":
      return <svg {...commonProps}><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></svg>;
    case "sparkles":
      return <svg {...commonProps}><path d="m12 3-1.2 3.3a4 4 0 0 1-2.5 2.5L5 10l3.3 1.2a4 4 0 0 1 2.5 2.5L12 17l1.2-3.3a4 4 0 0 1 2.5-2.5L19 10l-3.3-1.2a4 4 0 0 1-2.5-2.5L12 3Z"/><path d="m5 16-.5 1.4A2.5 2.5 0 0 1 3 19l1.5.6A2.5 2.5 0 0 1 6 21l.5-1.4A2.5 2.5 0 0 1 8 18l-1.5-.6A2.5 2.5 0 0 1 5 16Z"/></svg>;
    case "table":
      return <svg {...commonProps}><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M9 9v11"/></svg>;
  }
}
