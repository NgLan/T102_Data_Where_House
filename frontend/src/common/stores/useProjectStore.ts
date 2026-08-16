/**
 * Zustand Store quản lý thông tin Project và trạng thái HITL Pop-up Modal
 */

import { create } from 'zustand';

interface ProjectState {
  projectId: string | null;
  domain: string;
  targetDialect: string;
  activeTableName: string | null;
  isHitlModalOpen: boolean;
  
  setProjectInfo: (id: string, domain: string, dialect: string) => void;
  /**
   * Cập nhật thông tin mô tả của dự án mà KHÔNG đụng tới projectId.
   * Dùng ở màn hình khởi tạo khi hệ thống chưa có API tạo dự án thật — tránh ghi đè
   * projectId hợp lệ bằng giá trị giả, khiến mọi lời gọi API sau đó hỏng.
   */
  setProjectMeta: (domain: string, dialect: string) => void;
  setDataModel: (dataModel: ActiveDataModel | null) => void;
  openHitlModal: (tableName: string) => void;
  closeHitlModal: () => void;
}

/**
 * Hook Zustand store quản lý Project và HITL Modal State
 */
export const useProjectStore = create<ProjectState>((set) => ({
  projectId: null,
  domain: 'ride',
  targetDialect: 'PostgreSQL (Standard DWH)',
  activeTableName: null,
  isHitlModalOpen: false,

  setProjectInfo: (id, domain, dialect) => set({ projectId: id, domain, targetDialect: dialect }),

  setProjectMeta: (domain, dialect) => set({ domain, targetDialect: dialect }),

  setDataModel: (dataModel) => set({ dataModel }),

  openHitlModal: (tableName) => set({ activeTableName: tableName, isHitlModalOpen: true }),
  
  closeHitlModal: () => set({ isHitlModalOpen: false, activeTableName: null }),
}));
