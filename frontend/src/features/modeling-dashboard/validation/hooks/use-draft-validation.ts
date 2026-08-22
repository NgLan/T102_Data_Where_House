"use client";

import { useEffect, useRef, useState } from "react";
import { handleApiError, type DataModelValidationIssueResponse } from "@/api";
import { requestDraftValidation } from "../services/draft-validation-api";

const VALIDATION_DEBOUNCE_MS = 500;

/** Debounce validation và bỏ qua response thuộc draft cũ. */
export function useDraftValidation(
  projectId: string,
  dbml: string,
  parseError: string | null,
) {
  const [issues, setIssues] = useState<DataModelValidationIssueResponse[]>([]);
  const [isValidating, setIsValidating] = useState(false);
  const [errorCode, setErrorCode] = useState<string | null>(null);
  const requestSequence = useRef(0);

  useEffect(() => {
    const sequence = ++requestSequence.current;
    if (!projectId || parseError || !dbml.trim()) {
      void Promise.resolve().then(() => {
        setIssues([]);
        setIsValidating(false);
      });
      return;
    }
    const timer = window.setTimeout(async () => {
      setIsValidating(true);
      try {
        const nextIssues = await requestDraftValidation(projectId, dbml);
        if (sequence === requestSequence.current) {
          setIssues(nextIssues);
          setErrorCode(null);
        }
      } catch (error: unknown) {
        if (sequence === requestSequence.current) {
          setErrorCode(handleApiError(error, { shouldNotify: false }).errorCode);
        }
      } finally {
        if (sequence === requestSequence.current) setIsValidating(false);
      }
    }, VALIDATION_DEBOUNCE_MS);
    return () => window.clearTimeout(timer);
  }, [dbml, parseError, projectId]);

  const hasErrors = issues.some((issue) => issue.severity === "ERROR");
  return { issues, hasErrors, isValidating, errorCode };
}
