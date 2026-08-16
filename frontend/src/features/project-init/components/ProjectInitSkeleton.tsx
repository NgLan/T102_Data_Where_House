import { Skeleton } from "@/common/components/ui/skeleton";

/** Skeleton cho lần tải project và danh sách source đầu tiên.
 * @returns Trạng thái chờ có cùng bố cục với màn hình Project Init.
 */
export function ProjectInitSkeleton() {
  return <div className="space-y-5" aria-busy="true">
    <Skeleton className="h-20 w-full" />
    <Skeleton className="h-80 w-full" />
    <Skeleton className="h-64 w-full" />
  </div>;
}
