import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import commonVi from "./locales/vi/common.json";
import errorsVi from "./locales/vi/errors.json";
import notificationsVi from "./locales/vi/notifications.json";
import projectInitVi from "./locales/vi/project-init.json";
import modelingDashboardVi from "./locales/vi/modeling-dashboard.json";
import modelingWorkspaceVi from "./locales/vi/modeling-workspace.json";
import modelInspectorVi from "./locales/vi/model-inspector.json";
import aiInsightsVi from "./locales/vi/ai-insights.json";
import aiChatVi from "./locales/vi/ai-chat.json";
import proposalReviewVi from "./locales/vi/proposal-review.json";
import sandboxDeploymentVi from "./locales/vi/sandbox-deployment.json";
import projectManagementVi from "./locales/vi/project-management.json";
import authVi from "./locales/vi/auth.json";

import commonEn from "./locales/en/common.json";
import errorsEn from "./locales/en/errors.json";
import notificationsEn from "./locales/en/notifications.json";
import projectInitEn from "./locales/en/project-init.json";
import modelingDashboardEn from "./locales/en/modeling-dashboard.json";
import modelingWorkspaceEn from "./locales/en/modeling-workspace.json";
import modelInspectorEn from "./locales/en/model-inspector.json";
import aiInsightsEn from "./locales/en/ai-insights.json";
import aiChatEn from "./locales/en/ai-chat.json";
import proposalReviewEn from "./locales/en/proposal-review.json";
import sandboxDeploymentEn from "./locales/en/sandbox-deployment.json";
import projectManagementEn from "./locales/en/project-management.json";
import authEn from "./locales/en/auth.json";

/** Namespace mặc định cho nội dung dùng chung. */
export const defaultNS = "common";

/** Tài nguyên VI/EN đã đăng ký theo namespace feature. */
export const resources = {
  vi: {
    common: commonVi,
    errors: errorsVi,
    notifications: notificationsVi,
    "project-init": projectInitVi,
    "modeling-dashboard": modelingDashboardVi,
    "modeling-workspace": modelingWorkspaceVi,
    "model-inspector": modelInspectorVi,
    "ai-insights": aiInsightsVi,
    "ai-chat": aiChatVi,
    "proposal-review": proposalReviewVi,
    "sandbox-deployment": sandboxDeploymentVi,
    "project-management": projectManagementVi,
    auth: authVi,
  },
  en: {
    common: commonEn,
    errors: errorsEn,
    notifications: notificationsEn,
    "project-init": projectInitEn,
    "modeling-dashboard": modelingDashboardEn,
    "modeling-workspace": modelingWorkspaceEn,
    "model-inspector": modelInspectorEn,
    "ai-insights": aiInsightsEn,
    "ai-chat": aiChatEn,
    "proposal-review": proposalReviewEn,
    "sandbox-deployment": sandboxDeploymentEn,
    "project-management": projectManagementEn,
    auth: authEn,
  },
} as const;

if (!i18n.isInitialized) {
  i18n.use(initReactI18next).init({
    resources,
    lng: "vi",
    fallbackLng: "vi",
    defaultNS,
    interpolation: {
      escapeValue: false,
    },
  });
} else if (process.env.NODE_ENV === "development") {
  // HMR Hot Reload: Tự động cập nhật bản dịch khi sửa file JSON trong môi trường dev
  for (const [lng, namespaces] of Object.entries(resources)) {
    for (const [ns, bundle] of Object.entries(namespaces)) {
      i18n.addResourceBundle(lng, ns, bundle, true, true);
    }
  }
  i18n.emit("loaded");
  i18n.emit("languageChanged", i18n.language);
}

export default i18n;
