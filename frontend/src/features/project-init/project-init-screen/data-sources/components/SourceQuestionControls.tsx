import { useTranslation } from "react-i18next";
import type {
  SourceConfirmationQuestionType,
  SourceCoverageCandidateResponse,
} from "@/api";
import { SourceDirectConfirmation } from "./SourceDirectConfirmation";
import { SourceSelectionForm } from "./SourceSelectionForm";

interface Props {
  questionType?: SourceConfirmationQuestionType | null;
  groupName: string;
  candidates: SourceCoverageCandidateResponse[];
  selected?: string;
  disabled: boolean;
  onSelect: (id: string) => void;
  onConfirm: (id: string) => void;
  onReject: () => void;
}

/** Chọn đúng interaction contract từ question_type do backend cung cấp. */
export function SourceQuestionControls(props: Props) {
  const { t } = useTranslation("project-init");
  if (props.questionType === "SINGLE_FIELD_SELECTION") {
    return <SourceSelectionForm {...selectionProps(props)}
      confirmLabel={t("BTN_CONFIRM_SELECTION")}
      rejectLabel={t("BTN_NO_FIELD_SUITABLE")} />;
  }
  if (props.questionType === "BUSINESS_SEMANTIC_CHOICE") {
    return <SourceSelectionForm {...selectionProps(props)}
      confirmLabel={t("BTN_CONFIRM_SELECTION")}
      rejectLabel={t("BTN_NO_OPTION_SUITABLE")} />;
  }
  const isDirect = props.questionType === "FIELD_SET_CONFIRMATION"
    || props.questionType === "SINGLE_CANDIDATE_CONFIRMATION"
    || props.questionType === "RELATIONSHIP_CONFIRMATION";
  const candidate = props.candidates[0];
  if (!isDirect || !candidate) {
    return <p role="alert" className="mt-3 text-xs text-destructive">
      {t("TXT_CONFIRMATION_TYPE_ERROR")}
    </p>;
  }
  const labels = directLabels(props.questionType, t);
  return <SourceDirectConfirmation candidate={candidate} disabled={props.disabled}
    confirmLabel={labels.confirm} rejectLabel={labels.reject}
    onConfirm={props.onConfirm} onReject={props.onReject} />;
}

function selectionProps(props: Props) {
  return {
    groupName: props.groupName, candidates: props.candidates, selected: props.selected,
    disabled: props.disabled, onSelect: props.onSelect,
    onConfirm: props.onConfirm, onReject: props.onReject,
  };
}

function directLabels(questionType: Props["questionType"], t: (key: string) => string) {
  if (questionType === "FIELD_SET_CONFIRMATION") {
    return { confirm: t("BTN_USE_FIELDS"), reject: t("BTN_FIELDS_NOT_SUITABLE") };
  }
  if (questionType === "RELATIONSHIP_CONFIRMATION") {
    return { confirm: t("BTN_USE_RELATIONSHIP"), reject: t("BTN_RELATIONSHIP_NOT_SUITABLE") };
  }
  return { confirm: t("BTN_USE_THIS_FIELD"), reject: t("BTN_FIELD_NOT_SUITABLE") };
}
