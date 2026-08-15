/**
 * Zustand Store quản lý thông tin Project, Data Model hiện hành và trạng thái HITL Pop-up Modal
 */

import { create } from 'zustand';

/** Thông tin mô hình dữ liệu hiện hành lấy từ Backend */
export interface ActiveDataModel {
  id: string;
  dbml: string;
  revision: number;
}

interface ProjectState {
  projectId: string | null;
  domain: string;
  targetDialect: string;
  activeTableName: string | null;
  isHitlModalOpen: boolean;

  /** Mô hình dữ liệu hiện hành của dự án — nguồn dữ liệu chung cho DDL Export & Proposal Diff */
  dataModel: ActiveDataModel | null;

  setProjectInfo: (id: string, domain: string, dialect: string) => void;
  setDataModel: (dataModel: ActiveDataModel | null) => void;
  openHitlModal: (tableName: string) => void;
  closeHitlModal: () => void;
}

/**
 * Hook Zustand store quản lý Project, Data Model và HITL Modal State
 */
export const useProjectStore = create<ProjectState>((set) => ({
  projectId: process.env.NEXT_PUBLIC_DEMO_PROJECT_ID ?? null,
  domain: 'ride',
  targetDialect: 'PostgreSQL (Standard DWH)',
  activeTableName: null,
  isHitlModalOpen: false,
  dataModel: null,

  setProjectInfo: (id, domain, dialect) => set({ projectId: id, domain, targetDialect: dialect }),

  setDataModel: (dataModel) => set({ dataModel }),

  openHitlModal: (tableName) => set({ activeTableName: tableName, isHitlModalOpen: true }),

  closeHitlModal: () => set({ isHitlModalOpen: false, activeTableName: null }),
}));
