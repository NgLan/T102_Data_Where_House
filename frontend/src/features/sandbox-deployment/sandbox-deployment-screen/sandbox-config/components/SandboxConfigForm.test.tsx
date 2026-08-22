// @vitest-environment jsdom

import { zodResolver } from "@hookform/resolvers/zod";
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useForm } from "react-hook-form";
import { afterEach, describe, expect, it, vi } from "vitest";
import {
  DEFAULT_SANDBOX_CONFIG,
  sandboxConfigFormSchema,
  type SandboxConfigFormValues,
} from "../schemas/sandbox-config-form-schema";
import { SandboxConfigForm } from "./SandboxConfigForm";

vi.mock("react-i18next", () => ({
  initReactI18next: { type: "3rdParty", init: vi.fn() },
  useTranslation: () => ({ t: (key: string) => key }),
}));
afterEach(cleanup);

describe("SandboxConfigForm", () => {
  it("hiển thị validation error ngay dưới field", async () => {
    const onValid = vi.fn();
    render(<Harness onValid={onValid} />);
    const host = screen.getByRole("textbox", { name: "HOST_LABEL" });
    await userEvent.clear(host);
    await userEvent.click(screen.getByRole("button", { name: "BTN_SAVE_CONFIG" }));
    expect(await screen.findByText("MSG_HOST_INVALID")).toBeInTheDocument();
    expect(onValid).not.toHaveBeenCalled();
  });
});

function Harness({ onValid }: { onValid: () => void }) {
  const form = useForm<SandboxConfigFormValues>({
    defaultValues: DEFAULT_SANDBOX_CONFIG,
    resolver: zodResolver(sandboxConfigFormSchema),
  });
  return (
    <SandboxConfigForm
      form={form}
      connectionLatencyMs={null}
      connectionStatus="idle"
      isSaving={false}
      isTestingConnection={false}
      onSave={form.handleSubmit(onValid)}
      onTestConnection={vi.fn()}
    />
  );
}
