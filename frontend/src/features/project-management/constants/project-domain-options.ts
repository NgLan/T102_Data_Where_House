/** Domain options được hỗ trợ bởi form tạo Project. */
export const PROJECT_DOMAIN_OPTIONS = [
  "RIDE",
  "ECOMMERCE",
  "BANKING",
  "CUSTOM",
] as const;

/** Domain mặc định là option đầu tiên trong danh sách công bố. */
export const DEFAULT_PROJECT_DOMAIN = PROJECT_DOMAIN_OPTIONS[0].toLowerCase();
