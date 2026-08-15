'use client';

import { Building2, Database, FileText, Sparkles } from 'lucide-react';
import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { Button } from '@/common/components/ui/button';
import { NativeSelect, NativeSelectOption } from '@/common/components/ui/native-select';
import { Textarea } from '@/common/components/ui/textarea';

export interface ProjectInitCardProps {
  domain: string;
  onDomainChange: (value: string) => void;
  dialect: string;
  onDialectChange: (value: string) => void;
  description: string;
  onDescriptionChange: (value: string) => void;
}

/** Hiển thị form ngữ cảnh nghiệp vụ và hệ quản trị dữ liệu đích.
 * @param props Giá trị form và callback cập nhật từ feature hook.
 * @returns Form cấu hình dự án dùng primitive shadcn.
 */
export function ProjectInitCard(props: ProjectInitCardProps) {
  const { t } = useTranslation('project-init');
  const suggestions = [t('TXT_SUGGESTION_TRIPS'), t('TXT_SUGGESTION_REVENUE'), t('TXT_SUGGESTION_CANCELLATION')];
  const handleSuggestion = (suggestion: string) => {
    props.onDescriptionChange(props.description ? `${props.description} ${suggestion}` : suggestion);
  };
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
          ['PostgreSQL (Standard DWH)', t('TXT_DIALECT_POSTGRESQL')], ['Snowflake', t('TXT_DIALECT_SNOWFLAKE')],
          ['BigQuery', t('TXT_DIALECT_BIGQUERY')], ['ClickHouse', t('TXT_DIALECT_CLICKHOUSE')],
        ]} />
      </div>
      <div className="space-y-2">
        <div className="flex flex-wrap items-center justify-between gap-2 text-xs font-bold text-slate-700">
          <label htmlFor="business-description" className="flex items-center gap-1.5"><FileText className="size-3.5 text-violet-600" />{t('DESCRIPTION_LABEL')}</label>
          <span className="flex items-center gap-1 text-[11px] font-normal text-slate-400"><Sparkles className="size-3 text-amber-500" />{t('TXT_AI_DESCRIPTION_HINT')}</span>
        </div>
        <Textarea id="business-description" rows={3} value={props.description} placeholder={t('DESCRIPTION_PLACEHOLDER')} onChange={(event) => props.onDescriptionChange(event.target.value)} />
        <div className="flex flex-wrap items-center gap-1.5"><span className="text-[11px] font-semibold text-slate-400">{t('TXT_QUICK_SUGGESTIONS')}</span>{suggestions.map((suggestion) => <Button key={suggestion} type="button" size="xs" variant="outline" onClick={() => handleSuggestion(suggestion)}>+ {suggestion}</Button>)}</div>
      </div>
    </div>
  );
}

interface SelectFieldProps {
  icon: ReactNode;
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: Array<[string, string]>;
}

function SelectField({ icon, label, value, onChange, options }: SelectFieldProps) {
  return <label className="space-y-1.5 text-xs font-bold text-slate-700"><span className="flex items-center gap-1.5 [&_svg]:size-3.5">{icon}{label}</span><NativeSelect className="w-full" value={value} onChange={(event) => onChange(event.target.value)}>{options.map(([optionValue, optionLabel]) => <NativeSelectOption key={optionValue} value={optionValue}>{optionLabel}</NativeSelectOption>)}</NativeSelect></label>;
}
