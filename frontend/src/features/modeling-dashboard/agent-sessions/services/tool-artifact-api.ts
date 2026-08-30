import { downloadBlob } from "@/common/browser/download-text-file";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8001/api/v1";

export async function downloadToolArtifact(input: {
  sessionId: string;
  toolResultEventId: string;
  filename: string;
}): Promise<void> {
  const path = `/sessions/${encodeURIComponent(input.sessionId)}/events/${encodeURIComponent(input.toolResultEventId)}/artifact`;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: "include",
    headers: { Accept: "text/markdown, text/plain" },
  });
  if (!response.ok) throw new Error("TOOL_ARTIFACT_DOWNLOAD_FAILED");
  downloadBlob(await response.blob(), input.filename);
}
