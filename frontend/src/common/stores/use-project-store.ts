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
  
  openHitlModal: (tableName) => set({ activeTableName: tableName, isHitlModalOpen: true }),
  
  closeHitlModal: () => set({ isHitlModalOpen: false, activeTableName: null }),
}));
