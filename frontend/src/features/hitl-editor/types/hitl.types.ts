/**
 * Types & Interfaces cho Feature HITL Editor, AI Re-prompting Chat & Review Đề xuất Thay đổi
 */

export interface ColumnAttribute {
  id: string;
  name: string;
  dataType: string;
  keyType: 'PK' | 'FK' | 'NONE';
  isNullable: boolean;
}

export interface ChatMessage {
  id: string;
  sender: 'ai' | 'user';
  text: string;
  timestamp: string;
}

/** Trạng thái đề xuất thay đổi — khớp enum DataModelChangeStatus của Backend */
export type ProposalStatus = 'PROPOSED' | 'ACCEPTED' | 'REJECTED' | 'CONFLICTED';

/** Thông tin tóm tắt một đề xuất thay đổi (dùng cho danh sách) */
export interface ChangeProposalSummaryDto {
  id: string;
  data_model_id: string;
  user_id: string;
  base_revision: number;
  status: ProposalStatus;
  created_at: string;
  updated_at: string;
}

/** Chi tiết đề xuất thay đổi kèm DBML hiện hành để dựng khung so sánh khác biệt (UC6.1) */
export interface ChangeProposalDetailDto extends ChangeProposalSummaryDto {
  proposed_dbml: string;
  current_dbml: string;
  current_revision: number;
  is_outdated: boolean;
}

/** Chế độ hiển thị khung so sánh khác biệt */
export type DiffViewMode = 'unified' | 'split';
