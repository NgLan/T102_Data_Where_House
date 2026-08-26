import { beforeEach, describe, expect, it, vi } from "vitest";
import { toast } from "sonner";
import {
  notifyAppError,
  notifyAppInfo,
  notifyAppSuccess,
  notifyAppWarning,
} from "./app-notification";

vi.mock("sonner", () => ({
  toast: { error: vi.fn(), success: vi.fn(), warning: vi.fn(), info: vi.fn() },
}));

describe("app-notification", () => {
  beforeEach(() => vi.clearAllMocks());

  it("ủy quyền các loại thông báo cho Sonner", () => {
    const notification = { title: "Title", message: "Message" };
    notifyAppSuccess(notification);
    notifyAppError(notification);
    notifyAppWarning(notification);
    notifyAppInfo(notification);
    expect(toast.success).toHaveBeenCalledWith("Title", { description: "Message" });
    expect(toast.error).toHaveBeenCalledOnce();
    expect(toast.warning).toHaveBeenCalledOnce();
    expect(toast.info).toHaveBeenCalledOnce();
  });
});

