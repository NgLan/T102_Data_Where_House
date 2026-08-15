'use client';

/**
 * Single Page Container chính - chuyển trang mượt mà qua các bước
 * Integration các feature component với thiết kế cao cấp Modern AI Web App
 */

import React from 'react';
import { useScreenStore } from '@/common/stores/useScreenStore';
import { MainLayout } from '@/common/components/layout/MainLayout';
import { Sparkles, ArrowLeft, ArrowRight, Rocket, Database, Layers, ShieldCheck, CheckCircle2, Loader2 } from 'lucide-react';

// Feature 1: Project Init
import { useProjectInit } from '@/features/project-init/hooks/useProjectInit';
import { ProjectInitCard } from '@/features/project-init/components/ProjectInitCard';
import { ExcelDragDrop } from '@/features/project-init/components/ExcelDragDrop';
import { ExcelDataGrid } from '@/features/project-init/components/ExcelDataGrid';
import { MaskingToggle } from '@/features/project-init/components/MaskingToggle';

// Feature 2: Modeling Dashboard
import { useErdModeling } from '@/features/modeling-dashboard/hooks/useErdModeling';
import { useAiInsights } from '@/features/modeling-dashboard/hooks/useAiInsights';
import { DbmlCodeEditor } from '@/features/modeling-dashboard/components/DbmlCodeEditor';
import { ErdVisualCanvas } from '@/features/modeling-dashboard/components/ErdVisualCanvas';
import { AiInsightsWidget } from '@/features/modeling-dashboard/components/AiInsightsWidget';

// Feature 3: HITL Editor (Pop-up Modal)
import { HitlModal } from '@/features/hitl-editor/components/HitlModal';

// Feature 4: Sandbox Deployment
import { useSandboxDeploy } from '@/features/sandbox-deployment/hooks/useSandboxDeploy';
import { DdlCodeEditor } from '@/features/sandbox-deployment/components/DdlCodeEditor';
import { SandboxConfigCard } from '@/features/sandbox-deployment/components/SandboxConfigCard';

export default function HomePage() {
  const activeScreen = useScreenStore((state) => state.activeScreen);
  const setScreen = useScreenStore((state) => state.setScreen);

  // Hook Feature 1
  const {
    domain,
    setDomain,
    targetDialect,
    setTargetDialect,
    businessDescription,
    setBusinessDescription,
    isMaskingEnabled,
    setIsMaskingEnabled,
    excelFileName,
    excelRows,
    isAnalyzing,
    handleLoadSampleData,
    handleAnalyzeAndProceed,
  } = useProjectInit();

  // Hook Feature 2
  const {
    dbmlCode,
    setDbmlCode,
    tables,
    zoomLevel,
    handleZoomIn,
    handleZoomOut,
    handleTableDoubleClick,
  } = useErdModeling();

  const {
    isWidgetOpen,
    toggleWidget,
    selectedTableFilter,
    setSelectedTableFilter,
    insights,
    totalCount,
  } = useAiInsights();

  // Hook Feature 4
  const {
    ddlCode,
    setDdlCode,
    dialect,
    handleDialectChange,
    schemaName,
    tableCount,
    ddlWarnings,
    isGeneratingDdl,
    ddlErrorCode,
    revision,
    hasDataModel,
    hostConnection,
    setHostConnection,
    databaseSchema,
    setDatabaseSchema,
    logs,
    isDeploying,
    handleFormatDdl,
    handleCopyDdl,
    handleDownloadDdl,
    handleDownloadDoc,
    handleDeploySandbox,
    handleGenerateTestData,
  } = useSandboxDeploy();

  return (
    <MainLayout>
      {/* ============================================================
          MÀN HÌNH STEP 1: KHỞI TẠO & UPLOAD EXCEL
      ============================================================ */}
      {activeScreen === 'step1' && (
        <div className="w-full flex flex-col space-y-5 screen-animate">
          {/* Page Title Header */}
          <div className="flex items-center justify-between bg-white/80 backdrop-blur-md p-4 rounded-2xl border border-slate-200/80 shadow-xs">
            <div>
              <h1 className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-slate-900 via-blue-900 to-indigo-900 bg-clip-text text-transparent mb-0.5">
                Khởi tạo dự án & Nạp dữ liệu nguồn Excel
              </h1>
              <p className="text-xs text-slate-500 m-0">
                Tự động nhận diện cấu trúc Excel thô, bảo mật dữ liệu nhạy cảm & tự động kiến tạo Data Warehouse DWH
              </p>
            </div>
            <div className="hidden sm:flex items-center gap-2">
              <span className="text-[11px] font-bold px-3 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                ✨ Step 1 of 3
              </span>
            </div>
          </div>

          {/* Form Card: Project Init Settings */}
          <div className="bg-white/95 backdrop-blur-md border border-slate-200/90 rounded-2xl p-5 shadow-xs hover:shadow-md transition-all">
            <ProjectInitCard
              domain={domain}
              onDomainChange={setDomain}
              dialect={targetDialect}
              onDialectChange={setTargetDialect}
              description={businessDescription}
              onDescriptionChange={setBusinessDescription}
            />
          </div>

          {/* Card: Excel Upload + Data Preview Grid */}
          <div className="bg-white/95 backdrop-blur-md border border-slate-200/90 rounded-2xl p-5 shadow-xs hover:shadow-md transition-all space-y-4">
            <ExcelDragDrop onLoadSample={handleLoadSampleData} />
            <ExcelDataGrid fileName={excelFileName ?? ''} rows={excelRows} />
            <MaskingToggle isEnabled={isMaskingEnabled} onChange={setIsMaskingEnabled} />

            {/* Primary Action CTA: Step 1 → Step 2 */}
            <button
              onClick={handleAnalyzeAndProceed}
              disabled={isAnalyzing}
              className="w-full mt-5 py-3.5 px-6 glow-btn-primary disabled:opacity-60 disabled:cursor-not-allowed text-white font-bold text-sm rounded-xl border-none cursor-pointer transition-all duration-300 flex items-center justify-center gap-2.5 shadow-lg shadow-blue-500/25 active:scale-[0.99]"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin text-white" />
                  <span>AI Agents đang phân tích dữ liệu & dựng Schema DWH...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5 animate-bounce text-amber-300" />
                  <span>AI Agents Phân tích & Tự động dựng Datawarehouse (ERD Schema)</span>
                  <ArrowRight className="w-4 h-4 ml-1" />
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* ============================================================
          MÀN HÌNH STEP 2: ERD CANVAS & AI INSIGHTS
      ============================================================ */}
      {activeScreen === 'step2' && (
        <div className="w-full flex flex-col flex-1 space-y-4 screen-animate">
          {/* Page Title Header + Nav Buttons */}
          <div className="flex items-center justify-between bg-white/80 backdrop-blur-md px-5 py-3 rounded-2xl border border-slate-200/80 shadow-xs">
            <div>
              <h1 className="text-lg font-extrabold tracking-tight text-slate-900 mb-0.5">
                Mô hình ERD Data Warehouse (dbdiagram.io Layout)
              </h1>
              <p className="text-xs text-slate-500 m-0">
                Bố cục DSL Text + ERD Canvas kéo thả &nbsp;|&nbsp;{' '}
                <b className="text-blue-600">Đúp chuột (Double-click) vào bảng để tinh chỉnh HITL</b>
              </p>
            </div>

            {/* Navigation Stepper Buttons */}
            <div className="flex items-center gap-2.5 flex-shrink-0">
              <button
                onClick={() => setScreen('step1')}
                className="flex items-center gap-1.5 px-3.5 py-2 border border-slate-200/90 bg-white text-slate-700 rounded-xl text-xs font-semibold hover:bg-slate-100/80 transition cursor-pointer"
              >
                <ArrowLeft className="w-3.5 h-3.5" /> Cấu hình lại
              </button>
              <button
                onClick={() => setScreen('step3')}
                className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-xl text-xs font-bold transition cursor-pointer shadow-md shadow-blue-500/20"
              >
                <Rocket className="w-3.5 h-3.5" /> Chạy Sandbox →
              </button>
            </div>
          </div>

          {/* ERD Split Editor + Visual Canvas Layout */}
          <div className="flex gap-4 flex-1" style={{ minHeight: '520px' }}>
            <DbmlCodeEditor code={dbmlCode} onChange={setDbmlCode} />
            <ErdVisualCanvas
              tables={tables}
              zoomLevel={zoomLevel}
              onZoomIn={handleZoomIn}
              onZoomOut={handleZoomOut}
              onTableDoubleClick={handleTableDoubleClick}
            />
          </div>

          {/* Floating AI Insights Widget Drawer */}
          <AiInsightsWidget
            isOpen={isWidgetOpen}
            onToggle={toggleWidget}
            selectedFilter={selectedTableFilter}
            onFilterChange={setSelectedTableFilter}
            insights={insights}
            totalCount={totalCount}
          />
        </div>
      )}

      {/* ============================================================
          MÀN HÌNH STEP 3: XUẤT DDL & SANDBOX DEPLOYMENT
      ============================================================ */}
      {activeScreen === 'step3' && (
        <div className="w-full flex flex-col flex-1 space-y-4 screen-animate">
          {/* Page Title Header + Nav Buttons */}
          <div className="flex items-center justify-between bg-white/80 backdrop-blur-md px-5 py-3 rounded-2xl border border-slate-200/80 shadow-xs">
            <div>
              <h1 className="text-lg font-extrabold tracking-tight text-slate-900 mb-0.5">
                Xuất Code DDL & Deploy Sandbox Executable
              </h1>
              <p className="text-xs text-slate-500 m-0">
                Cho phép xem & trực tiếp chỉnh sửa code DDL mở rộng full chiều cao & thực thi trực tiếp trên Sandbox
              </p>
            </div>

            {/* Navigation Button */}
            <div className="flex-shrink-0">
              <button
                onClick={() => setScreen('step2')}
                className="flex items-center gap-1.5 px-4 py-2 border border-slate-200/90 bg-white text-slate-700 rounded-xl text-xs font-semibold hover:bg-slate-100/80 transition cursor-pointer"
              >
                <ArrowLeft className="w-3.5 h-3.5" /> Quay lại chỉnh sửa ERD
              </button>
            </div>
          </div>

          {/* DDL Code Editor + Sandbox Panel Layout */}
          <div className="flex gap-4 flex-1" style={{ height: 'calc(100vh - 170px)' }}>
            <DdlCodeEditor
              ddlCode={ddlCode}
              onChange={setDdlCode}
              dialect={dialect}
              onDialectChange={handleDialectChange}
              schemaName={schemaName}
              tableCount={tableCount}
              revision={revision}
              warnings={ddlWarnings}
              errorCode={ddlErrorCode}
              isGenerating={isGeneratingDdl}
              isDownloadDisabled={!hasDataModel || isGeneratingDdl}
              onFormat={handleFormatDdl}
              onCopy={handleCopyDdl}
              onDownloadDoc={handleDownloadDoc}
              onDownloadSql={handleDownloadDdl}
            />
            <SandboxConfigCard
              host={hostConnection}
              onHostChange={setHostConnection}
              database={databaseSchema}
              onDatabaseChange={setDatabaseSchema}
              logs={logs}
              isDeploying={isDeploying}
              onDeploy={handleDeploySandbox}
              onGenerateTestData={handleGenerateTestData}
            />
          </div>
        </div>
      )}

      {/* Pop-up Modal HITL (Kích hoạt khi double-click bảng ở Step 2) */}
      <HitlModal />
    </MainLayout>
  );
}

