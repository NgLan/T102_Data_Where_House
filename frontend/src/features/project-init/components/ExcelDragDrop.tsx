'use client';

import { CheckCircle2, FileSpreadsheet, UploadCloud, Zap } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { Button } from '@/common/components/ui/button';

export interface ExcelDragDropProps {
  onLoadSample: () => void;
}

/** Hiển thị vùng chọn dữ liệu nguồn và action nạp mẫu.
 * @param props Callback nạp bộ dữ liệu mẫu hiện hành.
 * @returns Vùng upload có thể kích hoạt bằng chuột hoặc bàn phím.
 */
export function ExcelDragDrop({ onLoadSample }: ExcelDragDropProps) {
  const { t } = useTranslation('project-init');
  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="flex items-center gap-1.5 text-xs font-bold text-slate-700"><FileSpreadsheet className="size-4 text-emerald-600" />{t('TXT_UPLOAD_LABEL')}</span>
        <Button type="button" size="sm" variant="outline" onClick={onLoadSample}><Zap />{t('BTN_LOAD_SAMPLE')}</Button>
      </div>
      <Button type="button" variant="outline" onClick={onLoadSample} className="group h-auto w-full flex-col gap-2 border-2 border-dashed p-6 hover:border-emerald-500 hover:bg-emerald-50/30">
        <span className="flex size-12 items-center justify-center rounded-2xl bg-emerald-100 text-emerald-600 transition group-hover:bg-emerald-500 group-hover:text-white"><UploadCloud className="size-6" /></span>
        <strong className="text-xs text-slate-800">{t('TXT_DROP_INSTRUCTION')}</strong>
        <span className="max-w-lg whitespace-normal text-[11px] font-normal leading-relaxed text-slate-400">{t('TXT_DROP_DESCRIPTION')}</span>
        <span className="flex flex-wrap items-center justify-center gap-2 text-[10px] text-slate-500"><span>.XLSX</span><span>.XLS</span><span>.CSV</span><span className="flex items-center gap-1 font-semibold text-emerald-600"><CheckCircle2 className="size-3" />{t('TXT_AUTO_DETECT')}</span></span>
      </Button>
    </div>
  );
}
