const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8001/api/v1";
const CLIENT_VERSION = "1.0.0";

export interface ApiResponse<T> {
  status: "success";
  code: number;
  message: string;
  data: T;
}

interface ApiErrorResponse {
  code: number;
  message: string;
  error_code: string;
}

export class ApiClientError extends Error {
  /** Khởi tạo lỗi API có mã nghiệp vụ ổn định. */
  constructor(
    message: string,
    public readonly errorCode: string,
    public readonly statusCode: number,
  ) {
    super(message);
    this.name = "ApiClientError";
  }
}

/** Tạo các header truy vết chuẩn cho mỗi request frontend. */
function createHeaders(): HeadersInit {
  return {
    Accept: "application/json",
    "Content-Type": "application/json",
    "X-Client-Version": CLIENT_VERSION,
    "X-Request-ID": crypto.randomUUID(),
  };
}

/** Chuyển response lỗi của backend thành lỗi client có cấu trúc. */
async function toApiError(response: Response): Promise<ApiClientError> {
  const fallback: ApiErrorResponse = {
    code: response.status,
    message: "Không thể kết nối dịch vụ sinh DDL.",
    error_code: "API_REQUEST_FAILED",
  };
  const body = (await response.json().catch(() => fallback)) as ApiErrorResponse;
  return new ApiClientError(body.message, body.error_code, body.code);
}

/** Gửi POST JSON đến backend và trả payload trong response envelope. */
export async function postJson<TRequest, TResponse>(
  path: string,
  body: TRequest,
  signal?: AbortSignal,
): Promise<TResponse> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: createHeaders(),
    body: JSON.stringify(body),
    signal,
  });
  if (!response.ok) {
    throw await toApiError(response);
  }
  const envelope = (await response.json()) as ApiResponse<TResponse>;
  return envelope.data;
}
