"use client";

import { useRef, useState } from "react";
import { FileUp } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/common/components/ui/button";
import { cn } from "@/common/lib/utils";

interface DataSourceUploadProps {
  disabled: boolean;
  isUploading: boolean;
  onUpload: (files: File[]) => void;
}

/** Vùng chọn CSV/DOCX; parsing và persistence hoàn toàn do Backend xử lý.
 * @param props Trạng thái vô hiệu hóa và callback nhận danh sách tệp.
 * @returns Input tệp và nút chọn CSV/DOCX.
 */
export function DataSourceUpload(props: DataSourceUploadProps) {
  const { t } = useTranslation("project-init");
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const select = (files: FileList | null) => {
    if (files?.length) props.onUpload(Array.from(files));
  };
  return (
    <div
      className={cn(
        "rounded-xl border border-dashed p-6 text-center transition-colors",
        isDragging && "border-primary bg-primary/5",
        props.disabled && "opacity-60",
      )}
      onDragEnter={(event) => {
        event.preventDefault();
        setIsDragging(true);
      }}
      onDragOver={(event) => event.preventDefault()}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(event) => {
        event.preventDefault();
        setIsDragging(false);
        if (!props.disabled) select(event.dataTransfer.files);
      }}
    >
      <FileUp
        className="mx-auto mb-3 size-8 text-muted-foreground"
        aria-hidden="true"
      />
      <p className="font-medium">{t("TXT_UPLOAD_TITLE")}</p>
      <p className="mt-1 text-sm text-muted-foreground">
        {t("TXT_UPLOAD_HELP")}
      </p>
      <input
        ref={inputRef}
        className="sr-only"
        type="file"
        multiple
        accept=".csv,.docx,text/csv,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        disabled={props.disabled}
        onChange={(event) => {
          select(event.target.files);
          event.target.value = "";
        }}
      />
      <Button
        className="mt-4"
        type="button"
        variant="outline"
        disabled={props.disabled}
        onClick={() => inputRef.current?.click()}
      >
        {props.isUploading ? t("MSG_UPLOADING") : t("BTN_CHOOSE_FILES")}
      </Button>
    </div>
  );
}
