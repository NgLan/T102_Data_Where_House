"use client";

import { useState } from "react";
import { FileSpreadsheet } from "lucide-react";
import { useTranslation } from "react-i18next";
import { FileDropzone } from "@/common/components/files/FileDropzone";

const SOURCE_ACCEPT = {
  "text/csv": [".csv"],
  "text/tab-separated-values": [".tsv"],
  "application/vnd.ms-excel": [".xls"],
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
  "text/markdown": [".md", ".markdown"],
  "application/sql": [".sql"],
};

interface DataSourceUploadProps {
  disabled: boolean;
  remainingSlots: number;
  onUpload: (files: File[]) => void;
}

/** Vùng upload source tabular được backend hỗ trợ. */
export function DataSourceUpload(props: DataSourceUploadProps) {
  const { t } = useTranslation("project-init");
  const [hasRejected, setHasRejected] = useState(false);
  return <div>
    <FileDropzone accept={SOURCE_ACCEPT} disabled={props.disabled}
      help={t("TXT_UPLOAD_CSV_HELP", { count: props.remainingSlots })} icon={FileSpreadsheet}
      maxFiles={20} maxSize={20 * 1024 * 1024} multiple
      title={t("TXT_UPLOAD_CSV_TITLE")} onReject={() => setHasRejected(true)}
      onAccept={(files) => { setHasRejected(false); props.onUpload(files); }} />
    {hasRejected && <p className="mt-2 text-sm text-destructive" role="alert">
      {t("TXT_CSV_REJECTED")}
    </p>}
  </div>;
}
