import { zAnswerProjectSessionClarificationBody } from "@/api";

/** Bổ sung validation chéo cho contract answer được sinh từ OpenAPI. */
export function createClarificationAnswerSchema(requiredMessage: string) {
  return zAnswerProjectSessionClarificationBody.superRefine((answer, context) => {
    const isMissingOption =
      answer.answer_type === "option" && answer.option_index == null;
    const isMissingCustom =
      answer.answer_type === "custom" && !answer.custom_answer?.trim();
    if (isMissingOption || isMissingCustom) {
      context.addIssue({
        code: "custom",
        message: requiredMessage,
        path: [isMissingOption ? "option_index" : "custom_answer"],
      });
    }
  });
}
