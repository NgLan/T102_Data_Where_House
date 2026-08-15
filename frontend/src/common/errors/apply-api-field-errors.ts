import type { ApiError, FieldError } from "./api-error";
import { notifyApiError } from "./handle-api-error";

/** Payload tương thích với `setError` của React Hook Form và form tương đương. */
export interface FormFieldError {
  type: "server";
  message: string;
}

/** Cấu hình ánh xạ field Backend sang tên field của form. */
export interface ApplyApiFieldErrorsOptions<TField extends string> {
  setError: (field: TField, error: FormFieldError) => void;
  resolveField: (backendField: string) => TField | null;
}

/** Kết quả mapping giúp feature biết field nào không thể hiển thị inline. */
export interface FieldErrorMappingResult {
  mapped: readonly FieldError[];
  unmapped: readonly FieldError[];
}

/** Đưa validation details vào form và fallback toast nếu có field không map được. */
export function applyApiFieldErrors<TField extends string>(
  error: ApiError,
  options: ApplyApiFieldErrorsOptions<TField>,
): FieldErrorMappingResult {
  const result = error.details.reduce<FieldErrorMappingResult>(
    (current, detail) => applyFieldError(detail, current, options),
    { mapped: [], unmapped: [] },
  );
  if (result.unmapped.length > 0) notifyApiError(error, true);
  return result;
}

/** Áp dụng một detail và tích lũy kết quả immutable. */
function applyFieldError<TField extends string>(
  detail: FieldError,
  result: FieldErrorMappingResult,
  options: ApplyApiFieldErrorsOptions<TField>,
): FieldErrorMappingResult {
  const field = options.resolveField(detail.field);
  if (!field) return { ...result, unmapped: [...result.unmapped, detail] };
  options.setError(field, { type: "server", message: detail.message });
  return { ...result, mapped: [...result.mapped, detail] };
}
