'use client';

import { Loader2, Sparkles } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { Button } from '@/common/components/ui/button';

export interface AnalyzeTriggerButtonProps {
  isAnalyzing: boolean;
  onAnalyze: () => void;
}

/** Hiển thị action bắt đầu phân tích dữ liệu nguồn.
 * @param props Trạng thái xử lý và callback phân tích.
 * @returns Nút shadcn có loading state rõ ràng.
 */
export function AnalyzeTriggerButton({ isAnalyzing, onAnalyze }: AnalyzeTriggerButtonProps) {
  const { t } = useTranslation('project-init');
  return (
    <Button type="button" size="lg" className="w-full" disabled={isAnalyzing} onClick={onAnalyze}>
      {isAnalyzing ? <Loader2 className="animate-spin" /> : <Sparkles />}
      {isAnalyzing ? t('MSG_ANALYZING') : t('BTN_ANALYZE')}
    </Button>
  );
}
