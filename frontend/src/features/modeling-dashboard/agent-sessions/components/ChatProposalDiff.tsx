import { AlignJustify, Columns2, GitCompare } from "lucide-react";
import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import type { ChangeProposalDetailResponse } from "@/api";
import {
  SplitDbmlDiff,
  UnifiedDbmlDiff,
} from "../../modeling-workspace/components/proposal-review/components/DbmlDiffViews";
import { diffLines } from "../../modeling-workspace/components/proposal-review/utils/dbml-text-diff";

export function ChatProposalDiff({
  proposal,
}: {
  proposal: ChangeProposalDetailResponse;
}) {
  const { t } = useTranslation("proposal-review");
  const [mode, setMode] = useState<"unified" | "split">("unified");
  const diff = useMemo(
    () => diffLines(proposal.current_dbml, proposal.proposed_dbml),
    [proposal],
  );
  return (
    <section className="mt-2 flex max-h-80 min-h-32 w-full flex-col overflow-hidden rounded-xl border border-slate-200 bg-slate-50 text-slate-900 shadow-xs dark:border-slate-800/90 dark:bg-[#080d1a] dark:text-slate-200 dark:shadow-inner">
      <div className="flex items-center justify-between border-b border-slate-200 bg-slate-100/90 px-2.5 py-1 text-[11px] dark:border-slate-800/80 dark:bg-slate-900/80">
        <div className="flex items-center gap-1.5 font-medium text-slate-700 dark:text-slate-300">
          <GitCompare className="size-3 text-emerald-600 dark:text-emerald-400" />
          <span className="text-[10.5px]">{t("TXT_DIFF_TITLE", { defaultValue: "Chi tiết thay đổi DBML" })}</span>
        </div>
        <button
          type="button"
          onClick={() => setMode((m) => (m === "unified" ? "split" : "unified"))}
          className="flex cursor-pointer items-center gap-1 rounded px-1.5 py-0.5 text-[10px] font-medium text-sky-600 hover:bg-slate-200 hover:text-sky-700 dark:text-sky-400 dark:hover:bg-slate-800 dark:hover:text-sky-300 transition-colors"
        >
          {mode === "unified" ? (
            <>
              <Columns2 className="size-3" />
              <span>{t("BTN_MODE_SPLIT", { defaultValue: "Cột đôi" })}</span>
            </>
          ) : (
            <>
              <AlignJustify className="size-3" />
              <span>{t("BTN_MODE_UNIFIED", { defaultValue: "Hợp nhất" })}</span>
            </>
          )}
        </button>
      </div>
      <div className="dark-scrollbar min-h-0 flex-1 overflow-auto">
        {mode === "unified" ? (
          <UnifiedDbmlDiff diff={diff} />
        ) : (
          <SplitDbmlDiff
            diff={diff}
            currentLabel={t("TXT_CURRENT_DBML")}
            proposedLabel={t("TXT_PROPOSED_DBML")}
          />
        )}
      </div>
    </section>
  );
}
