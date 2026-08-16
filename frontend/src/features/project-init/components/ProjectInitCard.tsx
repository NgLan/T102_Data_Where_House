/**
 * Presentation Component: Form khởi tạo dự án (Domain, Dialect, Mô tả)
 * Glass card thiết kế sang trọng với gợi ý prompt thông minh
 */

import React from 'react';
import { Building2, Database, FileText, Sparkles, Car, ShoppingCart, Landmark, Cpu } from 'lucide-react';
import { SelectField } from '@/features/modeling-dashboard/modeling-workspace/model-inspector/components/relationship-inspector/SelectField';

export interface ProjectInitCardProps {
  domain: string;
  onDomainChange: (val: string) => void;
  dialect: string;
  onDialectChange: (val: string) => void;
  description: string;
  onDescriptionChange: (val: string) => void;
}

const PROMPT_SUGGESTIONS = [
  '🚗 Quản lý lịch trình chuyến đi & thông tin tài xế',
  '💰 Tính tổng doanh thu theo khu vực & khuyến mãi',
  '📊 Phân tích tỷ lệ hủy chuyến theo khung giờ peak',
];

export const ProjectInitCard: React.FC<ProjectInitCardProps> = ({
  domain,
  onDomainChange,
  dialect,
  onDialectChange,
  description,
  onDescriptionChange,
}) => {
  return (
    <div className="space-y-4">
      <header className="flex items-center gap-2 border-b border-slate-100 pb-3">
        <span className="flex size-7 items-center justify-center rounded-lg bg-blue-100 text-xs font-bold text-blue-600">1</span>
        <div><h2 className="text-sm font-bold text-slate-800">{t('TXT_CONFIGURATION_TITLE')}</h2><p className="text-xs text-slate-400">{t('TXT_CONFIGURATION_SUBTITLE')}</p></div>
      </header>
      <div className="grid gap-4 md:grid-cols-2">
        <SelectField icon={<Building2 />} label={t('DOMAIN_LABEL')} value={props.domain} onChange={props.onDomainChange} options={[
          ['ride', t('TXT_DOMAIN_RIDE')], ['ecommerce', t('TXT_DOMAIN_ECOMMERCE')],
          ['banking', t('TXT_DOMAIN_BANKING')], ['custom', t('TXT_DOMAIN_CUSTOM')],
        ]} />
        <SelectField icon={<Database />} label={t('DIALECT_LABEL')} value={props.dialect} onChange={props.onDialectChange} options={[
          ['postgresql', t('TXT_DIALECT_POSTGRESQL')],
        ]} />
      </div>
      <div className="space-y-2">
        <div className="flex flex-wrap items-center justify-between gap-2 text-xs font-bold text-slate-700">
          <label htmlFor="business-description" className="flex items-center gap-1.5"><FileText className="size-3.5 text-violet-600" />{t('DESCRIPTION_LABEL')}</label>
          <span className="flex items-center gap-1 text-[11px] font-normal text-slate-400"><Sparkles className="size-3 text-amber-500" />{t('TXT_AI_DESCRIPTION_HINT')}</span>
        </div>
      </div>
    </div>
  );
};

