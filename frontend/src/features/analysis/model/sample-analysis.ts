import type { ModelAnalysis } from "./types";

export const SAMPLE_ANALYSIS: ModelAnalysis = {
  modelName: "Ride Analytics Warehouse",
  version: 12,
  generatedAt: "13:42, 13/08/2026",
  qualityScore: 92,
  summary:
    "Mô hình sao gồm một bảng sự kiện chuyến đi và ba bảng chiều. Thiết kế ưu tiên tính đúng của doanh thu, lịch sử tài xế và khả năng mở rộng báo cáo theo khách hàng.",
  tables: [
    {
      id: "fact-rides",
      name: "Fact_Rides",
      role: "Fact",
      grain:
        "Mỗi dòng tương ứng với một chuyến đi được đặt, kể cả chuyến hoàn thành hoặc bị hủy.",
      grainRationale:
        "Grain ở cấp chuyến đi cho phép cộng trực tiếp doanh thu, phí và số chuyến mà không làm trùng dữ liệu khi phân tích theo tài xế hoặc khách hàng.",
      keyDecisions: [
        {
          column: "ride_key",
          kind: "Primary key",
          rationale:
            "Dùng surrogate key để tách định danh kho dữ liệu khỏi ride_id của hệ thống nguồn và hỗ trợ nạp lại dữ liệu an toàn.",
        },
        {
          column: "driver_key",
          kind: "Foreign key",
          reference: "Dim_Driver.driver_key",
          rationale:
            "Liên kết tới phiên bản hồ sơ tài xế có hiệu lực tại thời điểm chuyến đi, phù hợp với Slowly Changing Dimension.",
        },
        {
          column: "customer_key",
          kind: "Foreign key",
          reference: "Dim_Customer.customer_key",
          rationale:
            "Giữ phân tích hành vi khách hàng ổn định khi mã khách hàng ở nguồn thay đổi hoặc được hợp nhất.",
        },
      ],
      warnings: [
        {
          code: "CRIT_FAN_TRAP",
          severity: "critical",
          title: "Nguy cơ Fan Trap với khuyến mãi",
          message:
            "Một chuyến đi có thể dùng nhiều ưu đãi. Join trực tiếp Fact_Rides với Dim_Promo có thể nhân đôi fare_amount khi tổng hợp.",
          recommendation:
            "Tạo Bridge_Ride_Promo và phân bổ discount_amount theo từng ưu đãi trước khi tính tổng.",
        },
        {
          code: "WARN_UNINDEXED_FK",
          severity: "warning",
          title: "Khóa ngoại chưa được tối ưu",
          message:
            "customer_key và driver_key có tần suất join cao nhưng chưa có chiến lược clustering hoặc index tương ứng.",
          recommendation:
            "Cluster bảng theo driver_key, customer_key và partition theo DATE(created_at).",
        },
      ],
    },
    {
      id: "dim-driver",
      name: "Dim_Driver",
      role: "Dimension",
      grain: "Mỗi dòng là một phiên bản lịch sử của một tài xế.",
      grainRationale:
        "Một tài xế có thể thay đổi hạng xe, khu vực hoạt động và trạng thái. Lưu theo phiên bản giúp báo cáo quá khứ không bị thay đổi.",
      keyDecisions: [
        {
          column: "driver_key",
          kind: "Primary key",
          rationale:
            "Surrogate key cho phép nhiều phiên bản của cùng driver_id nguồn tồn tại đồng thời theo SCD Type 2.",
        },
      ],
      warnings: [
        {
          code: "WARN_SCD_DATE_RANGE",
          severity: "warning",
          title: "Thiếu khoảng hiệu lực SCD",
          message:
            "Bảng chưa có valid_from, valid_to và is_current để xác định phiên bản hồ sơ tài xế.",
          recommendation:
            "Bổ sung ba trường kiểm soát hiệu lực và ràng buộc chỉ một bản ghi is_current cho mỗi driver_id.",
        },
      ],
    },
    {
      id: "dim-customer",
      name: "Dim_Customer",
      role: "Dimension",
      grain: "Mỗi dòng tương ứng với một khách hàng duy nhất.",
      grainRationale:
        "Hồ sơ khách hàng được gom về một định danh chuẩn để phân tích tần suất đặt chuyến và giá trị vòng đời.",
      keyDecisions: [
        {
          column: "customer_key",
          kind: "Primary key",
          rationale:
            "Surrogate key tránh dùng số điện thoại hoặc email làm định danh và giảm rủi ro khi thông tin cá nhân thay đổi.",
        },
      ],
      warnings: [
        {
          code: "INFO_PII_MASKING",
          severity: "info",
          title: "Dữ liệu cá nhân cần được bảo vệ",
          message:
            "phone_number và email là PII, không nên hiển thị trực tiếp trong môi trường phân tích dùng chung.",
          recommendation:
            "Mask dữ liệu ở lớp semantic, mã hóa khi lưu và giới hạn quyền truy cập theo vai trò.",
        },
      ],
    },
    {
      id: "dim-promo",
      name: "Dim_Promo",
      role: "Dimension",
      grain: "Mỗi dòng tương ứng với một chương trình khuyến mãi.",
      grainRationale:
        "Tách chương trình khỏi lần áp dụng giúp tái sử dụng cùng một ưu đãi cho nhiều chuyến và theo dõi thời gian hiệu lực.",
      keyDecisions: [
        {
          column: "promo_key",
          kind: "Primary key",
          rationale:
            "Surrogate key giữ liên kết ổn định khi mã khuyến mãi được đổi tên hoặc tái sử dụng ở hệ thống nguồn.",
        },
      ],
      warnings: [],
    },
  ],
};

/** Đếm tổng số cảnh báo trong toàn bộ mô hình. */
export function countWarnings(analysis: ModelAnalysis): number {
  return analysis.tables.reduce((total, table) => total + table.warnings.length, 0);
}

/** Đếm tổng số quyết định khóa trong toàn bộ mô hình. */
export function countKeyDecisions(analysis: ModelAnalysis): number {
  return analysis.tables.reduce((total, table) => total + table.keyDecisions.length, 0);
}
