import { describe, expect, it } from "vitest";
import {
  formatCalendarDate,
  formatFullDateTime,
  formatRelativeTime,
} from "./format-relative-time";

const mockT = (key: string, opts?: Record<string, unknown>) => {
  const map: Record<string, string> = {
    TIME_JUST_NOW: "Vừa xong",
    TIME_MINUTES_AGO: `${opts?.count} phút trước`,
    TIME_HOURS_AGO: `${opts?.count} giờ trước`,
    TIME_YESTERDAY: "Hôm qua",
    TIME_DAYS_AGO: `${opts?.count} ngày trước`,
  };
  return map[key] ?? key;
};

describe("formatRelativeTime", () => {
  it("trả về TIME_JUST_NOW khi dưới 1 phút", () => {
    const now = new Date();
    expect(formatRelativeTime(now, mockT)).toBe("Vừa xong");
  });

  it("trả về TIME_MINUTES_AGO khi dưới 1 giờ", () => {
    const tenMinsAgo = new Date(Date.now() - 10 * 60 * 1000);
    expect(formatRelativeTime(tenMinsAgo, mockT)).toBe("10 phút trước");
  });

  it("trả về TIME_HOURS_AGO khi dưới 24 giờ", () => {
    const threeHoursAgo = new Date(Date.now() - 3 * 3600 * 1000);
    expect(formatRelativeTime(threeHoursAgo, mockT)).toBe("3 giờ trước");
  });

  it("trả về TIME_YESTERDAY khi là 1 ngày trước", () => {
    const oneDayAgo = new Date(Date.now() - 25 * 3600 * 1000);
    expect(formatRelativeTime(oneDayAgo, mockT)).toBe("Hôm qua");
  });

  it("trả về TIME_DAYS_AGO khi dưới 7 ngày", () => {
    const fourDaysAgo = new Date(Date.now() - 4 * 24 * 3600 * 1000);
    expect(formatRelativeTime(fourDaysAgo, mockT)).toBe("4 ngày trước");
  });

  it("trả về ngày lịch khi vượt quá 7 ngày", () => {
    const oldDate = new Date(2025, 0, 15);
    expect(formatCalendarDate(oldDate, "vi")).toBe("15/01/2025");
  });

  it("trả về chuỗi rỗng khi chuỗi ngày không hợp lệ", () => {
    expect(formatRelativeTime("invalid-date", mockT)).toBe("");
    expect(formatCalendarDate("invalid-date")).toBe("");
    expect(formatFullDateTime("invalid-date")).toBe("");
  });
});
