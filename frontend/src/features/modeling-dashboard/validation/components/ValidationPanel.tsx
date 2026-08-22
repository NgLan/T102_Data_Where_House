"use client";

import { useState } from "react";
import type { DataModelValidationIssueResponse } from "@/api";
import { useCornerDrag } from "../hooks/use-corner-drag";
import { ValidationPopup } from "./ValidationPopup";
import { ValidationTriggerButton } from "./ValidationTriggerButton";

interface ValidationPanelProps {
  issues: DataModelValidationIssueResponse[];
  isValidating: boolean;
  errorCode: string | null;
  projectId: string;
  onSelectTable: (tableName: string) => void;
}

/** Widget Validation Engine có thể cầm kéo di chuyển trực tiếp theo chuột và tự hít vào 1 trong 4 góc. */
export function ValidationPanel(props: ValidationPanelProps) {
  const [isOpen, setIsOpen] = useState(false);

  const {
    rootRef,
    isDragging,
    isTop,
    isLeft,
    dragHandlers,
    containerStyle,
  } = useCornerDrag({
    projectId: props.projectId,
    onToggleOpen: () => setIsOpen((prev) => !prev),
    onClose: () => setIsOpen(false),
  });

  const hasErrors = props.issues.some((item) => item.severity === "ERROR");
  const hasWarnings = props.issues.some((item) => item.severity === "WARNING");

  return (
    <div
      ref={rootRef}
      style={containerStyle}
      className={`pointer-events-none fixed z-50 flex ${
        isTop ? "top-20 flex-col-reverse" : "bottom-6 flex-col"
      } ${isLeft ? "left-6 items-start" : "right-6 items-end"}`}
    >
      {isOpen && (
        <ValidationPopup
          issues={props.issues}
          errorCode={props.errorCode}
          isTop={isTop}
          isDragging={isDragging}
          dragHandlers={dragHandlers}
          onClose={() => setIsOpen(false)}
          onSelectTable={props.onSelectTable}
        />
      )}

      <ValidationTriggerButton
        isValidating={props.isValidating}
        hasErrors={hasErrors}
        hasWarnings={hasWarnings}
        totalIssues={props.issues.length}
        isDragging={isDragging}
        dragHandlers={dragHandlers}
      />
    </div>
  );
}
