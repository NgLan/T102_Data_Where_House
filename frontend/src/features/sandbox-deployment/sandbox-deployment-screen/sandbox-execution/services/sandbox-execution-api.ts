import {
  executeSandboxDdl as requestSandboxDdlExecution,
  requireApiData,
  type ExecuteDdlResponse,
} from "@/api";
import { createSandboxRequestOptions } from "../../services/sandbox-api-request-options";

interface ExecuteSandboxDdlInput {
  projectId: string;
  ddlScript: string;
  shouldResetSchema: boolean;
}

/** Thực thi DDL trên cấu hình Sandbox đã lưu của project. */
export async function executeSandboxDdl(
  input: ExecuteSandboxDdlInput,
): Promise<ExecuteDdlResponse> {
  const response = await requestSandboxDdlExecution({
    ...createSandboxRequestOptions(input.projectId),
    body: {
      ddl_script: input.ddlScript,
      reset_schema: input.shouldResetSchema,
    },
  });
  return requireApiData(response.data);
}
