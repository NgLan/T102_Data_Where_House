/** Kiểu chuyển động nhấp nháy của điểm nút dữ liệu. */
export type DataNodeAnimationType = "pulse" | "ping" | "twinkle";

/** Cấu hình thuộc tính của từng điểm nút dữ liệu trên ma trận. */
export interface DataNode {
  top: string;
  left: string;
  size: number;
  color: string;
  glow: string;
  animationType: DataNodeAnimationType;
  duration: string;
  delay: string;
  hasRing?: boolean;
}
