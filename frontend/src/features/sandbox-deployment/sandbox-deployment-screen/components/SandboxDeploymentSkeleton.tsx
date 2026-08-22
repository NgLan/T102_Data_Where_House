import { Skeleton } from "@/common/components/ui/skeleton";

/** Giữ ổn định layout trong lần tải config và DDL đầu tiên. */
export function SandboxDeploymentSkeleton() {
  return (
    <div className="grid min-h-[520px] gap-4 lg:grid-cols-[7fr_3fr]" aria-busy="true">
      <Skeleton className="h-full min-h-[520px] rounded-2xl" />
      <div className="space-y-4 rounded-2xl border p-5">
        <Skeleton className="h-6 w-2/3" />
        <Skeleton className="h-4 w-full" />
        <div className="grid grid-cols-2 gap-3">
          {Array.from({ length: 6 }, (_, index) => (
            <Skeleton key={index} className="h-14" />
          ))}
        </div>
        <Skeleton className="h-9 w-full" />
        <Skeleton className="h-56 w-full" />
      </div>
    </div>
  );
}
