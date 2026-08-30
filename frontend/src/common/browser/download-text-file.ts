interface TextFileDownload {
  filename: string;
  content: string;
  mimeType: "text/markdown" | "text/plain";
}

export function downloadTextFile(file: TextFileDownload): void {
  downloadBlob(
    new Blob([file.content], { type: `${file.mimeType};charset=utf-8` }),
    file.filename,
  );
}

export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  try {
    link.click();
  } finally {
    link.remove();
    URL.revokeObjectURL(url);
  }
}
