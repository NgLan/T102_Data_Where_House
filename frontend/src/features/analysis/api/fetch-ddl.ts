import { postJson } from "@/api/client";

import type { DdlDocument, DdlRequest } from "../model/ddl-types";

/** Yêu cầu backend sinh DDL từ phiên bản mô hình hiện tại. */
export function fetchDdl(
  request: DdlRequest,
  signal?: AbortSignal,
): Promise<DdlDocument> {
  return postJson<DdlRequest, DdlDocument>("/data-models/ddl", request, signal);
}
