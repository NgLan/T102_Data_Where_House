/** Sentinel chỉ dùng trong UI khi người dùng muốn nhập domain riêng. */
export const CUSTOM_PROJECT_DOMAIN = "__custom__";

/** Catalog lĩnh vực nghiệp vụ dùng chung giữa các form Project. */
export const PROJECT_DOMAIN_OPTIONS = [
  { value: "ride", labelKey: "TXT_DOMAIN_RIDE" },
  { value: "ecommerce", labelKey: "TXT_DOMAIN_ECOMMERCE" },
  { value: "retail", labelKey: "TXT_DOMAIN_RETAIL" },
  { value: "banking", labelKey: "TXT_DOMAIN_BANKING" },
  { value: "healthcare", labelKey: "TXT_DOMAIN_HEALTHCARE" },
  { value: "education", labelKey: "TXT_DOMAIN_EDUCATION" },
  { value: "logistics", labelKey: "TXT_DOMAIN_LOGISTICS" },
  { value: "manufacturing", labelKey: "TXT_DOMAIN_MANUFACTURING" },
  { value: "telecommunications", labelKey: "TXT_DOMAIN_TELECOMMUNICATIONS" },
  { value: "travel_hospitality", labelKey: "TXT_DOMAIN_TRAVEL_HOSPITALITY" },
  { value: CUSTOM_PROJECT_DOMAIN, labelKey: "TXT_DOMAIN_CUSTOM" },
] as const;

/** Domain mặc định giữ tương thích hành vi form hiện tại. */
export const DEFAULT_PROJECT_DOMAIN = PROJECT_DOMAIN_OPTIONS[0].value;
