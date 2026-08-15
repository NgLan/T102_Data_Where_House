'use client';

import { ShieldCheck } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { Button } from '@/common/components/ui/button';
import { cn } from '@/common/lib/utils';

export interface MaskingToggleProps {
  isEnabled: boolean;
  onChange: (value: boolean) => void;
}

/** Điều khiển trạng thái che dữ liệu nhạy cảm trước khi phân tích.
 * @param props Trạng thái hiện tại và callback thay đổi.
 * @returns Toggle truy cập được dựa trên shadcn Button.
 */
export function MaskingToggle({ isEnabled, onChange }: MaskingToggleProps) {
  const { t } = useTranslation('project-init');
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200/80 bg-slate-50/90 p-3">
      <div className="flex items-center gap-3">
        <span className={cn('flex size-8 items-center justify-center rounded-lg', isEnabled ? 'bg-indigo-100 text-indigo-600' : 'bg-slate-200 text-slate-400')}><ShieldCheck className="size-4" /></span>
        <div><p className="text-xs font-bold text-slate-800">{t('TXT_MASKING_TITLE')}</p><p className="text-[11px] text-slate-400">{t('TXT_MASKING_DESCRIPTION')}</p></div>
      </div>
      <Button type="button" role="switch" aria-checked={isEnabled} variant={isEnabled ? 'default' : 'outline'} size="sm" onClick={() => onChange(!isEnabled)}>{isEnabled ? t('TXT_PROTECTED') : t('TXT_OFF')}</Button>
    </div>
  );
}
