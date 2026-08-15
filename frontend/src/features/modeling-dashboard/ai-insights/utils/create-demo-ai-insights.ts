import type { TFunction } from "i18next";
import type { AIInsight } from "../types/ai-insight-types";

/** Tạo dữ liệu AI Insights minh họa đã được bản địa hóa.
 * @param t Hàm dịch của namespace modeling-dashboard.
 * @returns Danh sách insight demo dùng riêng cho presentation.
 * @remarks Thay bằng generated contract khi Backend công bố endpoint tương ứng.
 */
export function createDemoAIInsights(t: TFunction): AIInsight[] {
  return [
    {
      id: "ins_1",
      tableName: "Fact_Rides",
      severity: "info",
      title: t("TXT_INSIGHT_GRAIN_TITLE"),
      description: t("TXT_INSIGHT_GRAIN_DESCRIPTION"),
    },
    {
      id: "ins_2",
      tableName: "Fact_Rides",
      severity: "error",
      title: t("TXT_INSIGHT_FAN_TRAP_TITLE"),
      description: t("TXT_INSIGHT_FAN_TRAP_DESCRIPTION"),
    },
    {
      id: "ins_3",
      tableName: "Dim_Driver",
      severity: "warn",
      title: t("TXT_INSIGHT_KEY_TITLE"),
      description: t("TXT_INSIGHT_KEY_DESCRIPTION"),
    },
    {
      id: "ins_4",
      tableName: "Dim_Customer",
      severity: "warn",
      title: t("TXT_INSIGHT_INDEX_TITLE"),
      description: t("TXT_INSIGHT_INDEX_DESCRIPTION"),
    },
  ];
}
