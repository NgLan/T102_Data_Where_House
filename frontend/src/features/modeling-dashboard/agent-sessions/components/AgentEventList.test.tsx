// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { SessionEventResponse } from "@/api";
import { AgentEventList } from "./AgentEventList";

vi.mock("react-i18next", () => ({
  initReactI18next: { type: "3rdParty", init: vi.fn() },
  useTranslation: () => ({ t: (key: string) => key }),
}));

afterEach(cleanup);

describe("AgentEventList", () => {
  it("không hiển thị proposal khi Agent xác nhận không cần thay đổi", () => {
    const event: SessionEventResponse = {
      id: "82d4185c-0ce0-4755-a33c-03692c938036",
      session_id: "961e347e-9db7-47a6-8c79-35ea3c78ec2c",
      turn_id: "42513453-0105-4fa8-8344-b69b078815f2",
      role: "AGENT",
      type: "MESSAGE",
      content: "Mô hình hiện tại đã đáp ứng đầy đủ yêu cầu.",
      status: "SUCCESS",
      proposal_change_id: null,
      question_options: [],
      allow_custom_answer: false,
      answer_to_question_id: null,
      client_message_id: null,
      question_kind: null,
      tool_name: null,
      tool_status: null,
      artifact_id: null,
      artifact_filename: null,
      artifact_mime_type: null,
      sandbox_schema_name: null,
      sandbox_endpoint_risk: null,
      executed_statements: null,
      succeeded_statements: null,
      failed_statements: null,
      total_duration_ms: null,
      created_at: "2026-08-24T00:00:00Z",
    };

    render(
      <AgentEventList events={[event]} isSending={false} projectId="project-1" />,
    );

    expect(screen.getByText(event.content as string)).toBeInTheDocument();
    expect(screen.queryByText("TXT_PROPOSAL_READY")).not.toBeInTheDocument();
  });

  it("không render successful AGENT_RESULT thành chat bubble", () => {
    const event: SessionEventResponse = {
      id: "82d4185c-0ce0-4755-a33c-03692c938037",
      session_id: "961e347e-9db7-47a6-8c79-35ea3c78ec2c",
      turn_id: "42513453-0105-4fa8-8344-b69b078815f2",
      role: "AGENT",
      type: "AGENT_RESULT",
      content: "Technical audit payload",
      status: "SUCCESS",
      proposal_change_id: null,
      question_options: [],
      allow_custom_answer: false,
      answer_to_question_id: null,
      client_message_id: null,
      question_kind: null,
      tool_name: null,
      tool_status: null,
      artifact_id: null,
      artifact_filename: null,
      artifact_mime_type: null,
      sandbox_schema_name: null,
      sandbox_endpoint_risk: null,
      executed_statements: null,
      succeeded_statements: null,
      failed_statements: null,
      total_duration_ms: null,
      created_at: "2026-08-24T00:00:01Z",
    };

    render(
      <AgentEventList events={[event]} isSending={false} projectId="project-1" />,
    );

    expect(screen.queryByText("Technical audit payload")).not.toBeInTheDocument();
  });
});
