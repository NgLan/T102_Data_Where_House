/**
 * Types & Interfaces cho Feature HITL Editor & AI Re-prompting Chat
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

export type ProposalStatus = 'PENDING' | 'ACCEPTED' | 'REJECTED';
