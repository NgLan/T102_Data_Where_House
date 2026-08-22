interface TextFileDownload {
  filename: string;
  content: string;
  mimeType: "text/markdown" | "text/plain";
}

/** Tải một file UTF-8 bằng Blob URL và luôn giải phóng tài nguyên tạm. */
export function downloadTextFile(file: TextFileDownload): void {
  const blob = new Blob([file.content], {
    type: `${file.mimeType};charset=utf-8`,
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = file.filename;
  document.body.appendChild(link);
  try {
    link.click();
  } finally {
    link.remove();
    URL.revokeObjectURL(url);
  }
}
