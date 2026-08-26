import { useTranslation } from "react-i18next";
import type { SourceCoverageAssessmentResponse } from "@/api";
import { Button } from "@/common/components/ui/button";

interface Props {
  assessment: SourceCoverageAssessmentResponse;
  disabled: boolean;
  onUploadRequest: () => void;
  onEditRequirement: () => void;
}

/** Missing capability card intentionally has no candidate or confirmation action. */
export function MissingSourceCard(props: Props) {
  const { t } = useTranslation("project-init");
  return (
    <article className="rounded-md border border-amber-300 bg-background/80 p-4 text-sm">
      <h4 className="font-medium">{props.assessment.title}</h4>
      <p className="mt-1 text-muted-foreground">{props.assessment.explanation}</p>
      <div className="mt-3 flex flex-wrap gap-2">
        <Button size="sm" type="button" disabled={props.disabled} onClick={props.onUploadRequest}>
          {t("BTN_UPLOAD_SOURCE")}
        </Button>
        <Button size="sm" type="button" variant="outline" disabled={props.disabled}
          onClick={props.onEditRequirement}>
          {t("BTN_EDIT_REQUIREMENT")}
        </Button>
      </div>
    </article>
  );
}
