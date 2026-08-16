import { MainLayout } from '@/common/components/layout/MainLayout';
import { ProjectManagementScreen } from '@/features/project-management';

/**
 * Trang chủ (/): Project Management Hub (Danh sách tất cả các dự án)
 * Đóng vai trò làm Dashboard quản lý danh sách dự án DWH, tìm kiếm và tạo dự án mới.
 */
export default function HomePage() {
  return (
    <MainLayout>
      <ProjectManagementScreen />
    </MainLayout>
  );
}

