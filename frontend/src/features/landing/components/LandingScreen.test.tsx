// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { LandingScreen } from "./LandingScreen";

const mocks = vi.hoisted(() => ({
  loginMutate: vi.fn(),
  registerMutate: vi.fn(),
  changeLanguage: vi.fn(),
  setTheme: vi.fn(),
}));

vi.mock("next/navigation", () => ({ useRouter: () => ({ push: vi.fn() }) }));
vi.mock("next-themes", () => ({ useTheme: () => ({ resolvedTheme: "dark", setTheme: mocks.setTheme }) }));
vi.mock("react-i18next", () => ({
  initReactI18next: { type: "3rdParty", init: vi.fn() },
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: { resolvedLanguage: "vi", changeLanguage: mocks.changeLanguage },
  }),
}));
vi.mock("@tanstack/react-query", () => ({
  useQueryClient: () => ({ clear: vi.fn(), invalidateQueries: vi.fn() }),
  useMutation: () => ({
    isPending: false,
    mutate: mocks.loginMutate,
  }),
}));

afterEach(cleanup);

describe("LandingScreen component", () => {
  beforeEach(() => {
    mocks.loginMutate.mockReset();
    mocks.registerMutate.mockReset();
    mocks.changeLanguage.mockReset();
    mocks.setTheme.mockReset();
  });

  it("renders hero section, video demo section, and documentation section", () => {
    render(<LandingScreen />);
    expect(screen.getByRole("heading", { name: "TXT_HERO_TITLE" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "TXT_DEMO_TITLE" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "TXT_DOCS_TITLE" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "TXT_FEATURES_TITLE" })).toBeInTheDocument();
  });

  it("has login link targeting /auth page", () => {
    render(<LandingScreen />);
    const loginLinks = screen.getAllByRole("link", { name: /BTN_LOGIN/ });
    expect(loginLinks.length).toBeGreaterThan(0);
    expect(loginLinks[0]).toHaveAttribute("href", "/auth");
  });

  it("renders documentation placeholder link with correct target and href", () => {
    render(<LandingScreen />);
    const docLink = screen.getByTitle("Documentation Placeholder Link");
    expect(docLink).toHaveAttribute("href", "https://docs.example.com");
    expect(docLink).toHaveAttribute("target", "_blank");
    expect(screen.getByText("TXT_DOCS_PLACEHOLDER_BADGE")).toBeInTheDocument();
  });

  it("toggles play state in video demo section", () => {
    render(<LandingScreen />);
    const playButton = screen.getByRole("button", { name: "TXT_DEMO_PLAY_OVERLAY" });
    fireEvent.click(playButton);
    expect(screen.getByRole("button", { name: "Pause" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Pause" }));
    expect(screen.getByRole("button", { name: "TXT_DEMO_PLAY_OVERLAY" })).toBeInTheDocument();
  });
});
