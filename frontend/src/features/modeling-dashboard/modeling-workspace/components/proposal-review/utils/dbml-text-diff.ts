import { diffArrays } from "diff";

export type DiffLineType = "added" | "removed" | "unchanged";

/** Một dòng trong kết quả so sánh kèm số dòng 1-based của hai phiên bản. */
export interface DiffLine {
  type: DiffLineType;
  text: string;
  oldLineNo: number | null;
  newLineNo: number | null;
}

/** So sánh DBML theo dòng bằng adapter quanh thư viện jsdiff. */
export function diffLines(original: string, revised: string): DiffLine[] {
  let oldLineNo = 1;
  let newLineNo = 1;
  return diffArrays(toLines(original), toLines(revised)).flatMap((change) =>
    change.value.map((text) => {
      const type = resolveDiffType(change.added, change.removed);
      const line = createDiffLine({ type, text, oldLineNo, newLineNo });
      if (type !== "added") oldLineNo += 1;
      if (type !== "removed") newLineNo += 1;
      return line;
    }),
  );
}

/** Đếm số dòng được thêm và xóa trong kết quả so sánh. */
export function countDiff(diff: readonly DiffLine[]): { added: number; removed: number } {
  return diff.reduce(
    (count, item) => ({
      added: count.added + Number(item.type === "added"),
      removed: count.removed + Number(item.type === "removed"),
    }),
    { added: 0, removed: 0 },
  );
}

/** Cho biết hai văn bản có thay đổi hay không. */
export function hasChanges(diff: readonly DiffLine[]): boolean {
  return diff.some((item) => item.type !== "unchanged");
}

function toLines(text: string): string[] {
  return text ? text.replace(/\r\n/g, "\n").split("\n") : [];
}

function resolveDiffType(added?: boolean, removed?: boolean): DiffLineType {
  if (added) return "added";
  if (removed) return "removed";
  return "unchanged";
}

function createDiffLine(input: {
  type: DiffLineType;
  text: string;
  oldLineNo: number;
  newLineNo: number;
}): DiffLine {
  return {
    type: input.type,
    text: input.text,
    oldLineNo: input.type === "added" ? null : input.oldLineNo,
    newLineNo: input.type === "removed" ? null : input.newLineNo,
  };
}
