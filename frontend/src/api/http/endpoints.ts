/** Endpoint legacy chỉ dành cho các operation chưa có trong generated SDK. */

export const API_ENDPOINTS = {
  REPROMPT_HITL: "/hitl/reprompt",
  ACCEPT_PROPOSAL: "/hitl/proposal/accept",
  EXECUTE_SANDBOX: "/sandbox/execute",
  SIMULATE_TEST_DATA: "/sandbox/simulate-data",
} as const;
