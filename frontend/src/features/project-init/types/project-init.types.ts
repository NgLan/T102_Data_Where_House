/**
 * Types & Interfaces dành riêng cho Feature Project Init
 */

export interface DomainOption {
  value: string;
  label: string;
}

export interface DialectOption {
  value: string;
  label: string;
}

export interface ProjectInitFormState {
  domain: string;
  targetDialect: string;
  businessDescription: string;
}
