"use client";

import type { ComponentType } from "react";
import { useDropzone, type Accept, type FileRejection } from "react-dropzone";
import { UploadCloud } from "lucide-react";
import { cn } from "@/common/lib/utils";

interface FileDropzoneProps {
  accept: Accept;
  disabled?: boolean;
  help: string;
  icon?: ComponentType<{ className?: string; "aria-hidden"?: boolean }>;
  maxFiles?: number;
  maxSize?: number;
  multiple?: boolean;
  title: string;
  onAccept: (files: File[]) => void;
  onReject: (rejections: FileRejection[]) => void;
}

/** Vùng chọn file dùng chung, hỗ trợ click, bàn phím và kéo thả. */
export function FileDropzone(props: FileDropzoneProps) {
  const Icon = props.icon ?? UploadCloud;
  const dropzone = useDropzone({
    accept: props.accept,
    disabled: props.disabled,
    maxFiles: props.maxFiles,
    maxSize: props.maxSize,
    multiple: props.multiple,
    onDropAccepted: props.onAccept,
    onDropRejected: props.onReject,
  });
  return (
    <div
      {...dropzone.getRootProps({ role: "button", "aria-label": props.title })}
      className={cn(
        "flex min-h-44 cursor-pointer flex-col items-center justify-center rounded-xl border border-dashed p-6 text-center transition-colors",
        "hover:border-primary hover:bg-primary/5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        dropzone.isDragActive && "border-primary bg-primary/5",
        props.disabled && "pointer-events-none cursor-not-allowed opacity-60",
      )}
    >
      <input {...dropzone.getInputProps()} />
      <Icon className="mb-3 size-8 text-muted-foreground" aria-hidden />
      <p className="font-medium">{props.title}</p>
      <p className="mt-1 text-sm text-muted-foreground">{props.help}</p>
    </div>
  );
}
