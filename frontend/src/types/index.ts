/**
 * Main types export file for the Logistics AI Dashboard.
 * Re-exports all type definitions for easy importing.
 */

// Core logistics types
export * from './logistics';

// API types
export * from './api';

// UI types
export * from './ui';

// Utility types
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

// Common generic types
export interface SelectOption<T = string> {
  value: T;
  label: string;
  disabled?: boolean;
}

export interface KeyValuePair<T = any> {
  key: string;
  value: T;
}

export interface Coordinates {
  latitude: number;
  longitude: number;
}

export interface TimeRange {
  start: string;
  end: string;
}

export interface Pagination {
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
}

export interface SortConfig {
  field: string;
  direction: 'asc' | 'desc';
}

export interface FilterConfig {
  field: string;
  operator: 'eq' | 'ne' | 'gt' | 'gte' | 'lt' | 'lte' | 'contains' | 'in';
  value: any;
}