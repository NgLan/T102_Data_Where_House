import { handleApiError } from '@/common/errors/handle-api-error';
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

client.interceptors.error.use((error, response) =>
  handleApiError(error, { status: response?.status }),
);

/** Shared generated client configured at the frontend application boundary. */
export { client as apiClient };
export * from './generated';
