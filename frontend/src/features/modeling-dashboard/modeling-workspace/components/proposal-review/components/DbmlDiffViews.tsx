import type { DiffLine } from "../utils/dbml-text-diff";

const LINE_STYLES: Record<DiffLine["type"], string> = {
  added: "bg-emerald-50 text-emerald-800 dark:bg-emerald-500/10 dark:text-emerald-300",
  removed: "bg-rose-50 text-rose-800 dark:bg-rose-500/10 dark:text-rose-300",
  unchanged: "text-slate-700 dark:text-slate-400",
};

const LINE_MARKERS: Record<DiffLine["type"], string> = {
  added: "+",
  removed: "-",
  unchanged: " ",
};

/** Hiển thị diff trên một cột với số dòng cũ và mới, tự động xuống dòng khi dài. */
export function UnifiedDbmlDiff({ diff }: { diff: DiffLine[] }) {
  return (
    <div className="dark-scrollbar flex-1 overflow-y-auto py-2 font-mono text-[12.5px] leading-relaxed">
      {diff.map((line, index) => (
        <div
          key={index}
          className={`flex items-start py-0.5 ${LINE_STYLES[line.type]}`}
        >
          <LineNumber value={line.oldLineNo} />
          <LineNumber value={line.newLineNo} />
          <span className="w-4 shrink-0 select-none font-bold">
            {LINE_MARKERS[line.type]}
          </span>
          <span className="min-w-0 flex-1 whitespace-pre-wrap break-all pr-4">
            {line.text || " "}
          </span>
        </div>
      ))}
    </div>
  );
}

/** Hiển thị DBML hiện tại và đề xuất trên hai cột song song, tự động wrap text và cuộn chung toàn bảng. */
export function SplitDbmlDiff(props: {
  diff: DiffLine[];
  currentLabel: string;
  proposedLabel: string;
}) {
  return (
    <div className="flex h-full min-h-0 flex-1 flex-col overflow-hidden">
      <div className="flex shrink-0 border-b border-slate-200 bg-slate-100/90 text-[11px] font-semibold text-slate-700 dark:border-slate-800 dark:bg-slate-900/80 dark:text-slate-300">
        <div className="min-w-0 basis-1/2 truncate border-r border-slate-200 px-3.5 py-2 dark:border-slate-800">
          {props.currentLabel}
        </div>
        <div className="min-w-0 basis-1/2 truncate px-3.5 py-2">
          {props.proposedLabel}
        </div>
      </div>
      <div className="dark-scrollbar min-h-0 flex-1 overflow-y-auto py-2 font-mono text-[12.5px] leading-relaxed">
        {props.diff.map((line, index) => (
          <div key={index} className="flex min-w-full">
            <DiffSide line={line} side="old" />
            <DiffSide line={line} side="new" />
          </div>
        ))}
      </div>
    </div>
  );
}

function DiffSide({ line, side }: { line: DiffLine; side: "old" | "new" }) {
  const isEmpty =
    side === "old" ? line.type === "added" : line.type === "removed";
  return (
    <div
      className={`flex min-w-0 basis-1/2 items-start py-0.5 ${
        side === "old"
          ? "border-r border-slate-200 dark:border-slate-800/60"
          : ""
      } ${
        isEmpty
          ? "bg-slate-100/50 dark:bg-slate-900/30"
          : LINE_STYLES[line.type]
      }`}
    >
      <LineNumber value={side === "old" ? line.oldLineNo : line.newLineNo} />
      <span className="min-w-0 flex-1 whitespace-pre-wrap break-all pr-3">
        {isEmpty ? "" : line.text || " "}
      </span>
    </div>
  );
}

function LineNumber({ value }: { value: number | null }) {
  return (
    <span className="w-10 shrink-0 select-none pr-2 text-right text-slate-400 dark:text-slate-600">
      {value ?? ""}
    </span>
  );
}
