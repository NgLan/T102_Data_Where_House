import {
  generateDataModelDdl as requestDataModelDdl,
  requireApiData,
  type DataModelDdlResponse,
} from "@/api";
import type { DdlDialect } from "../../../constants/supported-ddl-dialects";
import { createSandboxRequestOptions } from "../../services/sandbox-api-request-options";

/** Sinh DDL của revision Data Model hiện hành theo dialect được chọn. */
export async function generateDataModelDdl(
  projectId: string,
  dialect: DdlDialect,
): Promise<DataModelDdlResponse> {
  const response = await requestDataModelDdl({
    ...createSandboxRequestOptions(projectId, false),
    query: { db_type: dialect },
  });
  return requireApiData(response.data);
}
