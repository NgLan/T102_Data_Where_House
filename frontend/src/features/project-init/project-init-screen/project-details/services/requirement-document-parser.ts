import mammoth from "mammoth";

/** Đọc tài liệu Requirement hoàn toàn trong browser. */
export async function parseRequirementDocument(file: File): Promise<string> {
  const extension = file.name.toLowerCase().split(".").pop();
  if (extension === "docx") {
    const result = await mammoth.extractRawText({ arrayBuffer: await file.arrayBuffer() });
    return result.value.trim();
  }
  if (extension === "txt" || extension === "md") return (await file.text()).trim();
  throw new Error("INVALID_REQUIREMENT_DOCUMENT_FORMAT");
}
