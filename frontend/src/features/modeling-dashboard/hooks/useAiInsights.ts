/**
 * Custom Hook quản lý Widget AI Insights nổi & bộ lọc danh sách cảnh báo theo bảng
 */

import { useState, useMemo } from 'react';
import { InsightItemDto } from '@/api/model/erd.dto';

const INITIAL_INSIGHTS: InsightItemDto[] = [
  {
    id: 'ins_1',
    table_name: 'Fact_Rides',
    severity: 'info',
    title: 'Khái quát Grain:',
    description: 'Fact_Rides = "Mỗi dòng tương ứng 1 chuyến đi được đặt thành công/hủy"',
  },
  {
    id: 'ins_2',
    table_name: 'Fact_Rides',
    severity: 'error',
    title: 'Fan Trap Anti-pattern:',
    description: 'Quan hệ 1:N giữa Fact_Rides ↔ Dim_Promo gây nhân đôi số tiền giảm giá khi SUM.',
  },
  {
    id: 'ins_3',
    table_name: 'Dim_Driver',
    severity: 'warn',
    title: 'Missing Surrogate Key:',
    description: 'Bảng Dim_Driver đang dùng Natural Key. Gợi ý sinh driver_key INT.',
  },
  {
    id: 'ins_4',
    table_name: 'Dim_Customer',
    severity: 'warn',
    title: 'Unindexed Foreign Key:',
    description: 'Cột customer_key trong bảng Fact chưa được đánh Index.',
  },
];

export function useAiInsights() {
  const [isWidgetOpen, setIsWidgetOpen] = useState<boolean>(false);
  const [selectedTableFilter, setSelectedTableFilter] = useState<string>('ALL');
  const [insights] = useState<InsightItemDto[]>(INITIAL_INSIGHTS);

  const toggleWidget = () => setIsWidgetOpen((prev) => !prev);

  // Lọc danh sách theo bảng đã chọn
  const filteredInsights = useMemo(() => {
    if (selectedTableFilter === 'ALL') return insights;
    return insights.filter((item) => item.table_name === selectedTableFilter);
  }, [insights, selectedTableFilter]);

  return {
    isWidgetOpen,
    toggleWidget,
    selectedTableFilter,
    setSelectedTableFilter,
    insights: filteredInsights,
    totalCount: insights.length,
  };
}
