import type { DataNode } from "./types";

/** Danh sách tọa độ và thuộc tính của các điểm nút dữ liệu phát sáng. */
export const DATA_NODES: readonly DataNode[] = [
  // Góc trên bên trái
  { top: "8%", left: "10%", size: 6, color: "#ef4444", glow: "0 0 10px #ef4444", animationType: "pulse", duration: "3s", delay: "0.2s" },
  { top: "14%", left: "22%", size: 10, color: "#dc2626", glow: "0 0 14px #dc2626", animationType: "ping", duration: "2.8s", delay: "0.6s", hasRing: true },
  { top: "22%", left: "8%", size: 4, color: "#f87171", glow: "0 0 8px #f87171", animationType: "twinkle", duration: "2.1s", delay: "1.1s" },
  { top: "28%", left: "18%", size: 8, color: "#f97316", glow: "0 0 12px #f97316", animationType: "pulse", duration: "4.2s", delay: "0.4s" },
  { top: "36%", left: "6%", size: 5, color: "#ea580c", glow: "0 0 8px #ea580c", animationType: "twinkle", duration: "1.8s", delay: "1.5s" },
  { top: "42%", left: "15%", size: 9, color: "#b91c1c", glow: "0 0 12px #b91c1c", animationType: "pulse", duration: "3.6s", delay: "0.9s" },

  // Góc trên bên phải
  { top: "10%", left: "88%", size: 8, color: "#f43f5e", glow: "0 0 12px #f43f5e", animationType: "ping", duration: "3.2s", delay: "0.3s", hasRing: true },
  { top: "16%", left: "74%", size: 5, color: "#ef4444", glow: "0 0 8px #ef4444", animationType: "twinkle", duration: "2.4s", delay: "1.3s" },
  { top: "24%", left: "85%", size: 9, color: "#e11d48", glow: "0 0 14px #e11d48", animationType: "pulse", duration: "4.5s", delay: "0.7s" },
  { top: "32%", left: "78%", size: 4, color: "#fb7185", glow: "0 0 7px #fb7185", animationType: "twinkle", duration: "1.9s", delay: "2.0s" },
  { top: "38%", left: "92%", size: 7, color: "#ea580c", glow: "0 0 10px #ea580c", animationType: "pulse", duration: "3.1s", delay: "0.5s" },
  { top: "46%", left: "82%", size: 11, color: "#dc2626", glow: "0 0 16px #dc2626", animationType: "ping", duration: "3.5s", delay: "1.0s", hasRing: true },

  // Góc dưới bên trái
  { top: "60%", left: "10%", size: 7, color: "#f97316", glow: "0 0 10px #f97316", animationType: "pulse", duration: "3.8s", delay: "0.8s" },
  { top: "68%", left: "20%", size: 10, color: "#ef4444", glow: "0 0 15px #ef4444", animationType: "ping", duration: "2.6s", delay: "0.4s", hasRing: true },
  { top: "76%", left: "7%", size: 5, color: "#be123c", glow: "0 0 8px #be123c", animationType: "twinkle", duration: "2.2s", delay: "1.7s" },
  { top: "84%", left: "16%", size: 8, color: "#f43f5e", glow: "0 0 12px #f43f5e", animationType: "pulse", duration: "4.0s", delay: "1.2s" },
  { top: "90%", left: "26%", size: 4, color: "#f87171", glow: "0 0 7px #f87171", animationType: "twinkle", duration: "1.7s", delay: "0.9s" },

  // Góc dưới bên phải
  { top: "58%", left: "84%", size: 6, color: "#dc2626", glow: "0 0 10px #dc2626", animationType: "pulse", duration: "3.4s", delay: "0.6s" },
  { top: "66%", left: "91%", size: 9, color: "#f97316", glow: "0 0 14px #f97316", animationType: "ping", duration: "3.0s", delay: "1.4s", hasRing: true },
  { top: "74%", left: "80%", size: 5, color: "#fb7185", glow: "0 0 8px #fb7185", animationType: "twinkle", duration: "2.0s", delay: "0.5s" },
  { top: "82%", left: "88%", size: 11, color: "#ef4444", glow: "0 0 16px #ef4444", animationType: "pulse", duration: "4.8s", delay: "1.1s", hasRing: true },
  { top: "92%", left: "76%", size: 4, color: "#e11d48", glow: "0 0 7px #e11d48", animationType: "twinkle", duration: "2.3s", delay: "0.2s" },

  // Vùng lân cận trung tâm
  { top: "12%", left: "48%", size: 7, color: "#ef4444", glow: "0 0 10px #ef4444", animationType: "pulse", duration: "3.7s", delay: "0.4s" },
  { top: "88%", left: "52%", size: 8, color: "#dc2626", glow: "0 0 12px #dc2626", animationType: "pulse", duration: "3.3s", delay: "1.3s" },
  { top: "50%", left: "28%", size: 5, color: "#f97316", glow: "0 0 8px #f97316", animationType: "twinkle", duration: "2.5s", delay: "0.7s" },
  { top: "52%", left: "72%", size: 6, color: "#f43f5e", glow: "0 0 9px #f43f5e", animationType: "twinkle", duration: "2.2s", delay: "1.6s" },
];
