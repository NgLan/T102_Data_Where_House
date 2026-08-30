// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { ClarificationQuestionResponse } from "@/api";
import { AgentClarificationCard } from "./AgentClarificationCard";

vi.mock("react-i18next", () => ({
  initReactI18next: { type: "3rdParty", init: vi.fn() },
  useTranslation: () => ({ t: (key: string) => key }),
}));

const clarification: ClarificationQuestionResponse = {
  question_id: "a551a5d0-4bca-4bc1-a91a-8f929d67de80",
  session_id: "cd178f8d-dd01-4518-9af8-d2ac99126b75",
  turn_id: "b5030640-62e5-4436-9e51-5a2f356da367",
  question: "Bạn muốn phân tích theo mức thời gian nào?",
  options: ["Theo ngày", "Theo tháng", "Theo quý"],
  allow_custom_answer: true,
  reason: "Time granularity chưa được xác định.",
  question_kind: "CLARIFICATION",
  tool_name: null,
  endpoint_risk: null,
  schema_name: null,
  reset_schema: null,
  created_at: "2026-08-24T00:00:00Z",
};

afterEach(cleanup);

describe("AgentClarificationCard", () => {
  it("hiển thị các option có căn cứ và luôn có lựa chọn Khác", () => {
    render(
      <AgentClarificationCard
        clarification={clarification}
        isSubmitting={false}
        onSubmit={vi.fn()}
      />,
    );

    expect(screen.getByRole("button", { name: "Theo ngày" })).toBeEnabled();
    expect(screen.getByRole("button", { name: "Theo tháng" })).toBeEnabled();
    expect(
      screen.getByRole("button", { name: "TXT_CLARIFICATION_OTHER" }),
    ).toBeEnabled();
  });

  it("chỉ submit custom answer sau khi nội dung hợp lệ", () => {
    const onSubmit = vi.fn();
    render(
      <AgentClarificationCard
        clarification={clarification}
        isSubmitting={false}
        onSubmit={onSubmit}
      />,
    );
    fireEvent.click(
      screen.getByRole("button", { name: "TXT_CLARIFICATION_OTHER" }),
    );
    const submit = screen.getByRole("button", {
      name: /BTN_SUBMIT_CLARIFICATION/,
    });
    expect(submit).toBeDisabled();
    fireEvent.change(
      screen.getByPlaceholderText("CLARIFICATION_CUSTOM_PLACEHOLDER"),
      { target: { value: "Theo tuần" } },
    );
    fireEvent.click(submit);

    expect(onSubmit).toHaveBeenCalledWith({
      answer_type: "custom",
      custom_answer: "Theo tuần",
    });
  });

  it("submit đúng index của option được chọn", () => {
    const onSubmit = vi.fn();
    render(
      <AgentClarificationCard
        clarification={clarification}
        isSubmitting={false}
        onSubmit={onSubmit}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: "Theo quý" }));
    fireEvent.click(
      screen.getByRole("button", { name: /BTN_SUBMIT_CLARIFICATION/ }),
    );

    expect(onSubmit).toHaveBeenCalledWith({
      answer_type: "option",
      option_index: 2,
    });
  });
});
