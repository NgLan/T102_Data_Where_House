import { useTranslation } from "react-i18next";
import type {
  SourceCoverageCandidateResponse,
  SourceCoverageReferenceResponse,
} from "@/api";

interface Props {
  candidate: SourceCoverageCandidateResponse;
}

/** Hiển thị business label trước exact source evidence của một mapping. */
export function SourceCandidateDetails({ candidate }: Props) {
  const { t } = useTranslation("project-init");
  return <div className="space-y-2">
    <p className="font-medium">{candidate.label}</p>
    {candidate.references.map((reference, index) => (
      <div className="text-xs text-muted-foreground"
        key={`${sourceReferenceLabel(reference)}-${index}`}>
        {reference.role_label && <p className="font-medium text-foreground">
          {reference.role_label}
        </p>}
        <p><span>{t("TXT_SOURCE_EVIDENCE")}:</span>{" "}
          {sourceReferenceLabel(reference)}</p>
      </div>
    ))}
  </div>;
}

/** Tạo nhãn evidence thuần từ generated source reference. */
export function sourceReferenceLabel(reference: SourceCoverageReferenceResponse): string {
  if (reference.kind === "COLUMN") {
    return `${reference.source_name} · ${reference.table_name}.${reference.column_name}`;
  }
  return `${reference.source_name} · ${reference.from_column} → ${reference.to_column}`;
}
