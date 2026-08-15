'use client';

import { useRouter } from 'next/navigation';
import { useTranslation } from 'react-i18next';
import { MainLayout } from '@/common/components/layout/MainLayout';
import { createWorkflowHref } from '@/common/routing/workflow-routing';
import { useProjectInit } from '../hooks/use-project-init';
import { AnalyzeTriggerButton } from './AnalyzeTriggerButton';
import { ExcelDataGrid } from './ExcelDataGrid';
import { ExcelDragDrop } from './ExcelDragDrop';
import { MaskingToggle } from './MaskingToggle';
import { ProjectInitCard } from './ProjectInitCard';

/** Điều phối toàn bộ màn hình khởi tạo dự án.
 * @returns Feature screen gồm cấu hình, dữ liệu nguồn và action phân tích.
 */
export function ProjectInitScreen() {
  const { t } = useTranslation('project-init');
  const router = useRouter();
  const project = useProjectInit();
  const handleAnalyzeProject = async (): Promise<void> => {
    await project.analyzeProject();
    router.push(createWorkflowHref('modeling'));
  };
  return (
    <MainLayout>
      <div className="flex w-full flex-col space-y-5 animate-in fade-in slide-in-from-bottom-2 duration-300">
        <header className="flex items-center justify-between rounded-2xl border border-slate-200/80 bg-white/80 p-4 shadow-xs backdrop-blur-md">
          <div><h1 className="text-xl font-extrabold tracking-tight text-slate-900">{t('TXT_SCREEN_TITLE')}</h1><p className="text-xs text-slate-500">{t('TXT_SCREEN_SUBTITLE')}</p></div>
          <span className="hidden rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-[11px] font-bold text-blue-700 sm:inline">{t('TXT_STEP_PROGRESS')}</span>
        </header>
        <section className="space-y-4 rounded-2xl border border-slate-200/90 bg-white/95 p-5 shadow-xs">
          <ProjectInitCard domain={project.domain} onDomainChange={project.setDomain} dialect={project.targetDialect} onDialectChange={project.setTargetDialect} description={project.businessDescription} onDescriptionChange={project.setBusinessDescription} />
        </section>
        <section className="space-y-4 rounded-2xl border border-slate-200/90 bg-white/95 p-5 shadow-xs">
          <ExcelDragDrop onLoadSample={project.handleLoadSampleData} />
          <ExcelDataGrid fileName={project.excelFileName ?? ''} rows={project.excelRows} />
          <MaskingToggle isEnabled={project.isMaskingEnabled} onChange={project.setIsMaskingEnabled} />
          <AnalyzeTriggerButton isAnalyzing={project.isAnalyzing} onAnalyze={() => void handleAnalyzeProject()} />
        </section>
      </div>
    </MainLayout>
  );
}
