import { Skeleton } from "@/common/components/ui/skeleton";

const SKELETON_CARD_COUNT = 3;

/** Giữ ổn định bố cục danh sách trong lần tải đầu.
 * @returns Ba placeholder card có accessible busy state.
 */
export function ProjectListSkeleton() {
  return <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3" aria-busy="true">
    {Array.from({ length: SKELETON_CARD_COUNT }, (_, index) => (
      <div key={index} className="space-y-4 rounded-xl border bg-card p-5">
        <Skeleton className="h-5 w-2/3" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-4/5" />
        <Skeleton className="h-8 w-full" />
      </div>
    ))}
  </div>;
}
