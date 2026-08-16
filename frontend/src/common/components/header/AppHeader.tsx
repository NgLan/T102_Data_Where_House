/**
 * Pure Presentation Component: Top Navigation Bar - 3 bước chuyển màn hình
 * Glassmorphic navigation header với Stepper Progress & AI Status indicator
 */

import React from 'react';
import { ScreenStep } from '@/common/stores/useScreenStore';
import { cn } from '@/common/lib/utils';
import { Sparkles, Database, LayoutGrid, Code2, CheckCircle2, ArrowRight } from 'lucide-react';

export interface AppHeaderProps {
  activeScreen: ScreenStep;
  onSelectScreen: (step: ScreenStep) => void;
}

const NAV_ITEMS: { step: ScreenStep; stepNum: number; label: string; badge: string; icon: React.ReactNode }[] = [
  {
    step: 'step1',
    stepNum: 1,
    label: 'Khởi tạo & Excel Source',
    badge: 'Step 1',
    icon: <Database className="w-4 h-4" />,
  },
  {
    step: 'step2',
    stepNum: 2,
    label: 'ERD Canvas & AI Insights',
    badge: 'Step 2',
    icon: <LayoutGrid className="w-4 h-4" />,
  },
  {
    step: 'step3',
    stepNum: 3,
    label: 'Xuất DDL & Sandbox Deploy',
    badge: 'Step 3',
    icon: <Code2 className="w-4 h-4" />,
  },
];

export const AppHeader: React.FC<AppHeaderProps> = ({ activeScreen, onSelectScreen }) => {
  const getStepIndex = (step: ScreenStep) => {
    switch (step) {
      case 'step1': return 1;
      case 'step2': return 2;
      case 'step3': return 3;
      default: return 1;
    }
  };

  const currentIndex = getStepIndex(activeScreen);

  return (
    <header className="bg-white/90 backdrop-blur-md border-b border-slate-200/80 px-6 py-2.5 flex items-center justify-between flex-shrink-0 z-40 sticky top-0 shadow-xs">
      {/* Brand Logo */}
      <div className="flex items-center gap-3 pr-6 border-r border-slate-200">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-violet-600 flex items-center justify-center text-white shadow-md shadow-blue-500/25">
          <Sparkles className="w-5 h-5 animate-pulse" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="text-base font-bold tracking-tight bg-gradient-to-r from-slate-900 via-slate-800 to-blue-900 bg-clip-text text-transparent">
              DataModel AI
            </span>
            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-blue-50 text-blue-600 border border-blue-200/60">
              v2.4
            </span>
          </div>
          <p className="text-[11px] text-slate-400 font-medium m-0">
            Autonomous Data Warehouse Architect
          </p>
        </div>
      </div>

      {/* Stepper Progress Bar */}
      <nav className="flex items-center gap-2">
        {NAV_ITEMS.map(({ step, stepNum, label, badge, icon }, idx) => {
          const isActive = activeScreen === step;
          const isPassed = currentIndex > stepNum;

          return (
            <React.Fragment key={step}>
              <button
                onClick={() => onSelectScreen(step)}
                className={cn(
                  'flex items-center gap-2.5 px-3.5 py-2 rounded-xl text-xs font-semibold cursor-pointer transition-all duration-200 border border-transparent',
                  isActive
                    ? 'bg-blue-50 text-blue-700 border-blue-200/80 shadow-xs font-bold'
                    : isPassed
                    ? 'bg-slate-50 text-slate-700 hover:bg-slate-100/80 hover:text-slate-900'
                    : 'text-slate-400 hover:text-slate-600 hover:bg-slate-50'
                )}
              >
                <div
                  className={cn(
                    'w-6 h-6 rounded-lg flex items-center justify-center text-[11px] font-bold transition-all',
                    isActive
                      ? 'bg-blue-600 text-white shadow-xs shadow-blue-500/30'
                      : isPassed
                      ? 'bg-emerald-500 text-white'
                      : 'bg-slate-200 text-slate-500'
                  )}
                >
                  {isPassed ? <CheckCircle2 className="w-3.5 h-3.5" /> : stepNum}
                </div>

                <span className="flex items-center gap-1.5">
                  <span className={isActive ? 'text-blue-600' : isPassed ? 'text-emerald-600' : 'text-slate-400'}>
                    {icon}
                  </span>
                  <span>{label}</span>
                </span>
              </button>

              {idx < NAV_ITEMS.length - 1 && (
                <ArrowRight className="w-3.5 h-3.5 text-slate-300 mx-0.5" />
              )}
            </React.Fragment>
          );
        })}
      </nav>

      {/* AI Status Badge */}
      <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200/70 text-emerald-700 px-3 py-1.5 rounded-full text-xs font-semibold">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
        </span>
        AI Agents Engine Ready
      </div>
    </header>
  );
};

