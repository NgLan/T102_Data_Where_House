'use client';

import { useState } from 'react';
import { useProjectStore } from '@/common/stores/use-project-store';
import type { ExcelPreviewRowDto } from '@/api/model/project.dto';

const SAMPLE_EXCEL_ROWS: ExcelPreviewRowDto[] = [
  { stt: 1, ride_id: '1001', driver_id: '501', customer_id: '8812', fare_amount: 150000, status: 'COMPLETED', created_at: '2026-08-01 08:30:00' },
  { stt: 2, ride_id: '1002', driver_id: '502', customer_id: '8815', fare_amount: 85000, status: 'COMPLETED', created_at: '2026-08-01 09:15:00' },
  { stt: 3, ride_id: '1003', driver_id: '501', customer_id: '8820', fare_amount: 45000, status: 'CANCELLED', created_at: '2026-08-01 10:00:00' },
  { stt: 4, ride_id: '1004', driver_id: '503', customer_id: '8812', fare_amount: 210000, status: 'COMPLETED', created_at: '2026-08-01 11:20:00' },
];

/**
 * Quản lý dữ liệu biểu mẫu và thao tác phân tích cho bước khởi tạo dự án.
 *
 * @returns Trạng thái biểu mẫu, dữ liệu xem trước và các hàm cập nhật tương ứng.
 * @remarks Hook chỉ xử lý nghiệp vụ; screen chịu trách nhiệm điều hướng sau khi phân tích thành công.
 */
export function useProjectInit() {
  const setProjectInfo = useProjectStore((state) => state.setProjectInfo);

  const [domain, setDomain] = useState<string>('ride');
  const [targetDialect, setTargetDialect] = useState<string>('PostgreSQL (Standard DWH)');
  const [businessDescription, setBusinessDescription] = useState<string>('');
  const [isMaskingEnabled, setIsMaskingEnabled] = useState<boolean>(true);
  
  const [excelFileName, setExcelFileName] = useState<string | null>('Sheet1_RawRides.xlsx');
  const [excelRows, setExcelRows] = useState<ExcelPreviewRowDto[]>(SAMPLE_EXCEL_ROWS);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);

  const handleLoadSampleData = () => {
    setExcelFileName('Sheet1_RawRides.xlsx');
    setExcelRows(SAMPLE_EXCEL_ROWS);
  };

  const analyzeProject = async (): Promise<void> => {
    setIsAnalyzing(true);
    setProjectInfo('proj_001', domain, targetDialect);

    await new Promise((resolve) => window.setTimeout(resolve, 400));
    setIsAnalyzing(false);
  };

  return {
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
    analyzeProject,
  };
}
