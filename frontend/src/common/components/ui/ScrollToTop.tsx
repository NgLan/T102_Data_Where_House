"use client";

import * as React from "react";
import { ArrowUp } from "lucide-react";
import { cn } from "@/common/lib/utils";
import { Button } from "@/common/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/common/components/ui/tooltip";

export interface ScrollToTopProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Khoảng cách cuộn tính từ đỉnh trang (px) để nút bắt đầu xuất hiện. Mặc định: 300 */
  threshold?: number;
  /** Kiểu cuộn khi nhấn: smooth hoặc auto. Mặc định: smooth */
  behavior?: ScrollBehavior;
  /** Nội dung nhãn tooltip hiển thị khi hover. */
  tooltip?: string;
  /** Tùy chọn icon tùy biến thay thế cho icon mũi tên mặc định. */
  icon?: React.ReactNode;
}

/** Component ScrollToTop chuẩn UI: Tự động hiện nút cuộn về đầu trang khi người dùng cuộn xuống. */
export function ScrollToTop({
  threshold = 300,
  behavior = "smooth",
  tooltip,
  icon,
  className,
  ...props
}: ScrollToTopProps) {
  const [visible, setVisible] = React.useState(false);

  React.useEffect(() => {
    const handleScroll = () => {
      if (typeof window !== "undefined") {
        setVisible(window.scrollY > threshold);
      }
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener("scroll", handleScroll);
  }, [threshold]);

  const scrollToTop = () => {
    if (typeof window !== "undefined") {
      window.scrollTo({
        top: 0,
        behavior,
      });
    }
  };

  const buttonElement = (
    <Button
      type="button"
      size="icon"
      variant="secondary"
      onClick={scrollToTop}
      aria-label={tooltip || "Scroll to top"}
      className={cn(
        "size-11 rounded-full shadow-lg border border-border/80 hover:shadow-xl hover:scale-110 active:scale-95 transition-all bg-background/90 backdrop-blur-md cursor-pointer",
        className
      )}
      {...props}
    >
      {icon ?? <ArrowUp className="size-5 text-primary" />}
    </Button>
  );

  return (
    <div
      className={cn(
        "fixed bottom-6 right-6 z-50 transition-all duration-300",
        visible
          ? "opacity-100 translate-y-0 pointer-events-auto"
          : "opacity-0 translate-y-4 pointer-events-none"
      )}
    >
      {tooltip ? (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>{buttonElement}</TooltipTrigger>
            <TooltipContent side="left">
              <span>{tooltip}</span>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      ) : (
        buttonElement
      )}
    </div>
  );
}
