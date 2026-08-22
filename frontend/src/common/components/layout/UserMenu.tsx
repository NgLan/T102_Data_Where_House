"use client";

import { ChevronDown, LogOut, Mail } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Avatar, AvatarFallback } from "@/common/components/ui/avatar";
import { Button } from "@/common/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/common/components/ui/dropdown-menu";
import { Skeleton } from "@/common/components/ui/skeleton";
import { useCurrentActorQuery } from "@/common/projects/project-queries";

/** Hiển thị actor MVP và menu tài khoản không giả lập logout.
 * @returns Skeleton khi tải hoặc dropdown hồ sơ actor hiện tại.
 */
export function UserMenu() {
  const { t } = useTranslation("common");
  const actorQuery = useCurrentActorQuery();
  if (actorQuery.isPending) return <Skeleton className="h-8 w-28" />;
  const actor = actorQuery.data;
  const username = actor?.username ?? t("TXT_USER_UNAVAILABLE");
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="h-10 gap-2 px-2" disabled={!actor}>
          <Avatar size="sm">
            <AvatarFallback>{initialsOf(username)}</AvatarFallback>
          </Avatar>
          <span className="hidden max-w-32 truncate sm:inline">{username}</span>
          <ChevronDown className="size-3.5" aria-hidden />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-64">
        <DropdownMenuLabel>{username}</DropdownMenuLabel>
        {actor && (
          <DropdownMenuItem disabled>
            <Mail />
            {actor.email}
          </DropdownMenuItem>
        )}
        <DropdownMenuSeparator />
        <DropdownMenuItem disabled>
          <LogOut />
          {t("BTN_LOGOUT_UNAVAILABLE")}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

function initialsOf(username: string): string {
  return username
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();
}
