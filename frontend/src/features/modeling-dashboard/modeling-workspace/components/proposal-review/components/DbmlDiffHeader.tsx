import { AlignJustify, Columns2, GitPullRequest } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { ChangeProposalDetailResponse } from "@/api";

export type DiffViewMode = "unified" | "split";

interface DbmlDiffHeaderProps {
  proposal: ChangeProposalDetailResponse;
  mode: DiffViewMode;
  addedCount: number;
  removedCount: number;
  onModeChange: (mode: DiffViewMode) => void;
}

/** Hiển thị tiêu đề đề xuất, thống kê dòng thay đổi và nút chuyển đổi chế độ xem diff. */
export function DbmlDiffHeader(props: DbmlDiffHeaderProps) {
  const { t } = useTranslation("proposal-review");
  const nextMode = props.mode === "unified" ? "split" : "unified";

  return (
    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200 bg-slate-50/90 px-3.5 py-2 dark:border-slate-800 dark:bg-slate-900/90">
      <div className="flex items-center gap-2 text-xs font-semibold text-slate-900 dark:text-slate-100">
        <GitPullRequest className="size-4 text-sky-600 dark:text-sky-400" />
        <span>{t("TXT_PROPOSAL_TITLE", { defaultValue: "DBML đề xuất" })}</span>
        <span className="rounded-full border border-sky-500/30 bg-sky-500/10 px-2.5 py-0.5 text-[10.5px] font-medium text-sky-700 dark:text-sky-300">
          {t(`MSG_STATUS_${props.proposal.status}`, {
            defaultValue: "Đang chờ duyệt",
          })}
        </span>
      </div>

      <div className="flex items-center gap-2.5">
        <span className="font-mono text-[11px] font-bold">
          <span className="text-emerald-600 dark:text-emerald-400">
            +{props.addedCount}
          </span>
          <span className="text-slate-400 dark:text-slate-600"> / </span>
          <span className="text-rose-600 dark:text-rose-400">
            −{props.removedCount}
          </span>
        </span>
        <button
          type="button"
          onClick={() => props.onModeChange(nextMode)}
          className="inline-flex cursor-pointer items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-2.5 py-1 text-[11px] font-semibold text-slate-700 shadow-xs transition-colors hover:bg-slate-100 hover:text-slate-900 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700 dark:hover:text-white"
        >
          {nextMode === "split" ? (
            <Columns2 className="size-3.5 text-sky-600 dark:text-sky-400" />
          ) : (
            <AlignJustify className="size-3.5 text-sky-600 dark:text-sky-400" />
          )}
          <span>
            {t(nextMode === "split" ? "BTN_MODE_SPLIT" : "BTN_MODE_UNIFIED", {
              defaultValue: nextMode === "split" ? "Tách đôi" : "Hợp nhất",
            })}
          </span>
        </button>
      </div>
    </div>
  );
}
