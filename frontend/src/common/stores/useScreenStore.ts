/**
 * Zustand Store quản lý màn hình hiện tại trong Single Page Application
 * Hỗ trợ 3 bước làm việc: 'step1' (Khởi tạo), 'step2' (ERD Canvas), 'step3' (Xuất DDL Sandbox)
 */

import { create } from 'zustand';

export type ScreenStep = 'step1' | 'step2' | 'step3';

interface ScreenState {
  activeScreen: ScreenStep;
  setScreen: (step: ScreenStep) => void;
}

/**
 * Hook Zustand store điều khiển màn hình làm việc
 */
export const useScreenStore = create<ScreenState>((set) => ({
  activeScreen: 'step1',
  setScreen: (step: ScreenStep) => set({ activeScreen: step }),
}));
