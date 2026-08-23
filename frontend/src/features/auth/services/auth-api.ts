import {
  apiClient,
  login,
  logout,
  register,
  requireApiData,
  type CurrentActorResponse,
  type LoginRequest,
  type RegisterRequest,
} from "@/api";

export async function loginUser(input: LoginRequest): Promise<CurrentActorResponse> {
  const response = await login({
    body: input,
    client: apiClient,
    meta: { shouldNotify: false },
    responseStyle: "fields",
    throwOnError: true,
  });
  return requireApiData(response.data);
}

export async function registerUser(input: RegisterRequest): Promise<CurrentActorResponse> {
  const response = await register({
    body: input,
    client: apiClient,
    meta: { shouldNotify: false },
    responseStyle: "fields",
    throwOnError: true,
  });
  return requireApiData(response.data);
}

export async function logoutUser(): Promise<void> {
  await logout({ client: apiClient, throwOnError: true });
}
