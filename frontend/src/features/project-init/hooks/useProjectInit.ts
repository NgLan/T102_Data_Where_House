/**
 * Custom Hook chứa toàn bộ State & Handlers cho Feature Project Init
 * Tách biệt hoàn toàn với presentation UI components
 */

import { useState } from 'react';
import { useScreenStore } from '@/common/stores/useScreenStore';
import { useProjectStore } from '@/common/stores/useProjectStore';
import { ExcelPreviewRowDto } from '@/api/model/project.dto';

// Dữ liệu mẫu khởi tạo mặc định Rides.xlsx
const SAMPLE_EXCEL_ROWS: ExcelPreviewRowDto[] = [
  { stt: 1, ride_id: '1001', driver_id: '501', customer_id: '8812', fare_amount: 150000, status: 'COMPLETED', created_at: '2026-08-01 08:30:00' },
  { stt: 2, ride_id: '1002', driver_id: '502', customer_id: '8815', fare_amount: 85000, status: 'COMPLETED', created_at: '2026-08-01 09:15:00' },
  { stt: 3, ride_id: '1003', driver_id: '501', customer_id: '8820', fare_amount: 45000, status: 'CANCELLED', created_at: '2026-08-01 10:00:00' },
  { stt: 4, ride_id: '1004', driver_id: '503', customer_id: '8812', fare_amount: 210000, status: 'COMPLETED', created_at: '2026-08-01 11:20:00' },
];

export function useProjectInit() {
  const setScreen = useScreenStore((state) => state.setScreen);
  const setProjectMeta = useProjectStore((state) => state.setProjectMeta);

  const [domain, setDomain] = useState<string>('ride');
  const [targetDialect, setTargetDialect] = useState<string>('PostgreSQL (Standard DWH)');
  const [businessDescription, setBusinessDescription] = useState<string>('');
  const [isMaskingEnabled, setIsMaskingEnabled] = useState<boolean>(true);
  
  const [excelFileName, setExcelFileName] = useState<string | null>('Sheet1_RawRides.xlsx');
  const [excelRows, setExcelRows] = useState<ExcelPreviewRowDto[]>(SAMPLE_EXCEL_ROWS);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);

  // Nạp dữ liệu mẫu Excel
  const handleLoadSampleData = () => {
    setExcelFileName('Sheet1_RawRides.xlsx');
    setExcelRows(SAMPLE_EXCEL_ROWS);
  };

  // Trigger kích hoạt AI Agent phân tích & chuyển qua màn hình ERD (Step 2)
  const handleAnalyzeAndProceed = async () => {
    setIsAnalyzing(true);
    // Lưu thông tin mô tả dự án vào store.
    // KHÔNG ghi đè projectId: hệ thống chưa có API tạo dự án thật, projectId hợp lệ đang
    // được nạp từ NEXT_PUBLIC_DEMO_PROJECT_ID nên ghi đè sẽ làm hỏng mọi lời gọi API sau đó.
    setProjectMeta(domain, targetDialect);
    
    // Giả lập thời gian xử lý AI
    setTimeout(() => {
      setIsAnalyzing(false);
      setScreen('step2');
    }, 400);
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
    handleAnalyzeAndProceed,
  };
}
