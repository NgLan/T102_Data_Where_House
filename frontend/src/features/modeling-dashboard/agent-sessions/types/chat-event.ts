import type { SessionEventResponse } from "@/api";

export type ChatDeliveryStatus = "sending" | "failed";

export type ChatEvent = SessionEventResponse & {
  deliveryStatus?: ChatDeliveryStatus;
};
