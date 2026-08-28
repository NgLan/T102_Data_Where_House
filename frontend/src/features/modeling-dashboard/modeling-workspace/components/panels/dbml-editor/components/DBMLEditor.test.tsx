// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { DBMLEditor, findTableBlockRange } from "./DBMLEditor";

vi.mock("react-i18next", () => ({ useTranslation: () => ({ t: (key: string) => key }) }));
afterEach(cleanup);

describe("findTableBlockRange", () => {
  it("tìm chính xác phạm vi của toàn bộ khối bảng Fact_DieuTri", () => {
    const code = `Table Dim_BenhNhan {
  id int [pk]
}

Table Fact_DieuTri {
    dieu_tri_key int [pk, increment]
    benh_nhan_key int [not null]
    thoi_gian_key int [not null]
    khoa_key int [not null]
    chuan_doan_key int [not null]
    so_ngay_dieu_tri int [not null]
}

Table Dim_Khoa {
  id int [pk]
}`;
    const range = findTableBlockRange(code, "Fact_DieuTri");
    expect(range).not.toBeNull();
    const extracted = code.slice(range!.startPos, range!.endPos);
    expect(extracted).toContain("Table Fact_DieuTri {");
    expect(extracted).toContain("so_ngay_dieu_tri int [not null]");
    expect(extracted.endsWith("}")).toBe(true);
    expect(extracted).not.toContain("Dim_Khoa");
    expect(extracted).not.toContain("Dim_BenhNhan");
  });
});

describe("DBMLEditor", () => {
  it("phát nội dung DBML mới từ editor khi không có proposalReview", () => {
    const onChange = vi.fn();
    render(<DBMLEditor code="Table users {}" parseError={null} onChange={onChange} />);
    const textarea = screen.getByRole("textbox", { name: "TXT_DBML_EDITOR" });
    expect(textarea).toBeInTheDocument();
    fireEvent.change(textarea, {
      target: { value: "Table accounts {}" },
    });
    expect(onChange).toHaveBeenCalledWith("Table accounts {}");
  });

  it("hiển thị proposalReview khi có đề xuất thay đổi", () => {
    render(
      <DBMLEditor
        code="Table users {}"
        parseError={null}
        onChange={vi.fn()}
        proposalReview={<div data-testid="proposal-diff">Proposal Diff Content</div>}
      />
    );
    expect(screen.getByTestId("proposal-diff")).toBeInTheDocument();
    expect(screen.queryByRole("textbox", { name: "TXT_DBML_EDITOR" })).not.toBeInTheDocument();
  });

  it("highlight toàn bộ khối Table khi nhận highlightTarget và tự tắt selection", () => {
    vi.useFakeTimers();
    const code = `Table Fact_DieuTri {\n  dieu_tri_key int [pk]\n  so_ngay_dieu_tri int\n}`;
    const { rerender } = render(
      <DBMLEditor
        code={code}
        parseError={null}
        onChange={vi.fn()}
        highlightTarget={null}
      />
    );

    const textarea = screen.getByRole("textbox", { name: "TXT_DBML_EDITOR" }) as HTMLTextAreaElement;
    expect(textarea.selectionStart).toBe(0);

    try {
      rerender(
        <DBMLEditor
          code={code}
          parseError={null}
          onChange={vi.fn()}
          highlightTarget={{ tableName: "Fact_DieuTri", triggerAt: Date.now() }}
        />
      );

      expect(textarea.selectionStart).toBe(0);
      expect(textarea.selectionEnd).toBe(code.length);

      vi.advanceTimersByTime(1600);
      expect(textarea.selectionStart).toBe(textarea.selectionEnd);
    } finally {
      vi.useRealTimers();
    }
  });

  it("hiển thị gạch chân lỗi và vạch đỏ trên thanh scroll khi có lỗi cú pháp", () => {
    const code = "Table users {\n  id in\n}";
    render(
      <DBMLEditor
        code={code}
        parseError="DATA_MODEL_DBML_SYNTAX_INVALID"
        syntaxErrors={[{ line: 2, column: 3, endLine: 2, endColumn: 8, message: "Expect a type" }]}
        onChange={vi.fn()}
      />
    );

    const scrollbarOverview = screen.getByLabelText("ARIA_ERROR_OVERVIEW_RULER");
    expect(scrollbarOverview).toBeInTheDocument();
    const errorMarkerButton = screen.getByTitle("TOOLTIP_ERROR_LINE");
    expect(errorMarkerButton).toBeInTheDocument();
  });
});
