// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { DBMLEditor } from "./DBMLEditor";

vi.mock("react-i18next", () => ({ useTranslation: () => ({ t: (key: string) => key }) }));
afterEach(cleanup);

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
});
