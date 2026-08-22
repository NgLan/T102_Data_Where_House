import type { ReactNode } from "react";

interface ProjectListFeedbackProps {
  icon: ReactNode;
  title: string;
  description: string;
  action: ReactNode;
}

/** Hiển thị một trạng thái phản hồi không có grid Project.
 * @param props Icon, nội dung và action phục hồi tương ứng.
 * @returns Empty/error/no-result state dùng chung trong project list.
 */
export function ProjectListFeedback(props: ProjectListFeedbackProps) {
  return (
    <section className="flex flex-col items-center gap-3 rounded-xl border border-dashed bg-card/50 p-12 text-center">
      <span className="text-primary">{props.icon}</span>
      <h2 className="font-semibold">{props.title}</h2>
      <p className="max-w-md text-sm text-muted-foreground">
        {props.description}
      </p>
      {props.action}
    </section>
  );
}
