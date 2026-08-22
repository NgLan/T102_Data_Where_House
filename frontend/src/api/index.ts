import { handleApiError } from './errors';
import { client } from './generated/client.gen';

const configuredBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8001/api/v1';
const backendBaseUrl = configuredBaseUrl.replace(/\/api\/v1\/?$/, '');

client.setConfig({
  baseUrl: backendBaseUrl,
  headers: {
    Accept: 'application/json',
    'X-Client-Version': '1.0.0',
  },
});

client.interceptors.request.use((request) => {
  request.headers.set('X-Request-ID', `req_${crypto.randomUUID()}`);
  return request;
});

/** Đọc cờ tắt toast mà caller gắn kèm qua `meta` của từng request. */
function readShouldNotify(options: unknown): boolean {
  const meta = (options as { meta?: { shouldNotify?: boolean } } | undefined)?.meta;
  return meta?.shouldNotify !== false;
}

// Caller nào tự dựng UI lỗi tại chỗ (khung chat Agent, empty state...) thì gắn
// `meta: { shouldNotify: false }` để không bị toast chồng lên thông báo inline.
client.interceptors.error.use((error, response, _request, options) =>
  handleApiError(error, {
    status: response?.status,
    shouldNotify: readShouldNotify(options),
  }),
);

/** Generated client dùng chung, được cấu hình tại application boundary của Frontend. */
export { client as apiClient };
export * from './generated';
export * from './api-data';
export * from './errors';
