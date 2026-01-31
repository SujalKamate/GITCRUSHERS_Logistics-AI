/**
 * UI-specific types for the Logistics AI Dashboard.
 * Defines component props, state, and UI-related interfaces.
 */

import { TruckStatus, TrafficLevel, LoadPriority, ControlLoopPhase } from './logistics';

// ============================================================================
// Component Props
// ============================================================================

export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
}

export interface LoadingProps extends BaseComponentProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
}

export interface ErrorProps extends BaseComponentProps {
  error: string | Error;
  retry?: () => void;
  showDetails?: boolean;
}

// ============================================================================
// Status Badge Types
// ============================================================================

export interface StatusBadgeProps extends BaseComponentProps {
  status: TruckStatus | TrafficLevel | LoadPriority | ControlLoopPhase | string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'outline' | 'solid';
}

export type StatusColorMap = {
  [key in TruckStatus]: {
    bg: string;
    text: string;
    border?: string;
  };
};

// ============================================================================
// Map Component Types
// ============================================================================

export interface MapProps extends BaseComponentProps {
  center?: [number, number]; // [lat, lng]
  zoom?: number;
  height?: string | number;
  trucks?: MapTruck[];
  routes?: MapRoute[];
  traffic?: MapTrafficSegment[];
  onTruckClick?: (truckId: string) => void;
  onRouteClick?: (routeId: string) => void;
  showControls?: boolean;
  showTraffic?: boolean;
}

export interface MapTruck {
  id: string;
  name: string;
  position: [number, number]; // [lat, lng]
  status: TruckStatus;
  heading?: number;
  speed?: number;
  loadId?: string;
}

export interface MapRoute {
  id: string;
  truckId: string;
  coordinates: [number, number][]; // Array of [lat, lng]
  color?: string;
  weight?: number;
  opacity?: number;
}

export interface MapTrafficSegment {
  id: string;
  coordinates: [number, number][];
  level: TrafficLevel;
  speed?: number;
  incident?: string;
}

// ============================================================================
// Chart Component Types
// ============================================================================

export interface ChartProps extends BaseComponentProps {
  data: any[];
  width?: number;
  height?: number;
  responsive?: boolean;
}

export interface LineChartProps extends ChartProps {
  xKey: string;
  yKey: string;
  color?: string;
  showGrid?: boolean;
  showTooltip?: boolean;
}

export interface BarChartProps extends ChartProps {
  xKey: string;
  yKey: string;
  color?: string;
  horizontal?: boolean;
}

export interface PieChartProps extends ChartProps {
  dataKey: string;
  nameKey: string;
  colors?: string[];
  showLabels?: boolean;
  showLegend?: boolean;
}

// ============================================================================
// Dashboard Layout Types
// ============================================================================

export interface DashboardLayoutProps extends BaseComponentProps {
  sidebar?: React.ReactNode;
  header?: React.ReactNode;
  footer?: React.ReactNode;
  sidebarCollapsed?: boolean;
  onSidebarToggle?: () => void;
}

export interface SidebarProps extends BaseComponentProps {
  collapsed?: boolean;
  onToggle?: () => void;
  items?: SidebarItem[];
}

export interface SidebarItem {
  id: string;
  label: string;
  icon?: React.ComponentType<{ className?: string }>;
  href?: string;
  onClick?: () => void;
  active?: boolean;
  badge?: string | number;
  children?: SidebarItem[];
}

// ============================================================================
// Data Table Types
// ============================================================================

export interface DataTableProps<T = any> extends BaseComponentProps {
  data: T[];
  columns: TableColumn<T>[];
  loading?: boolean;
  error?: string;
  pagination?: TablePagination;
  sorting?: TableSorting;
  filtering?: TableFiltering;
  selection?: TableSelection<T>;
  actions?: TableAction<T>[];
}

export interface TableColumn<T = any> {
  key: keyof T | string;
  title: string;
  width?: string | number;
  sortable?: boolean;
  filterable?: boolean;
  render?: (value: any, record: T, index: number) => React.ReactNode;
  align?: 'left' | 'center' | 'right';
}

export interface TablePagination {
  current: number;
  pageSize: number;
  total: number;
  showSizeChanger?: boolean;
  showQuickJumper?: boolean;
  onChange: (page: number, pageSize: number) => void;
}

export interface TableSorting {
  field?: string;
  order?: 'asc' | 'desc';
  onChange: (field: string, order: 'asc' | 'desc') => void;
}

export interface TableFiltering {
  filters: Record<string, any>;
  onChange: (filters: Record<string, any>) => void;
}

export interface TableSelection<T = any> {
  selectedRowKeys: string[];
  onChange: (selectedRowKeys: string[], selectedRows: T[]) => void;
  getCheckboxProps?: (record: T) => { disabled?: boolean };
}

export interface TableAction<T = any> {
  key: string;
  label: string;
  icon?: React.ComponentType<any>;
  onClick: (record: T) => void;
  disabled?: (record: T) => boolean;
  danger?: boolean;
}

// ============================================================================
// Form Types
// ============================================================================

export interface FormProps extends BaseComponentProps {
  onSubmit: (values: any) => void | Promise<void>;
  initialValues?: any;
  loading?: boolean;
  disabled?: boolean;
}

export interface FormFieldProps extends BaseComponentProps {
  name: string;
  label?: string;
  required?: boolean;
  disabled?: boolean;
  error?: string;
  help?: string;
}

export interface SelectOption {
  value: string | number;
  label: string;
  disabled?: boolean;
  group?: string;
}

// ============================================================================
// Modal Types
// ============================================================================

export interface ModalProps extends BaseComponentProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  closable?: boolean;
  maskClosable?: boolean;
  footer?: React.ReactNode;
}

export interface ConfirmModalProps extends Omit<ModalProps, 'footer'> {
  onConfirm: () => void | Promise<void>;
  onCancel?: () => void;
  confirmText?: string;
  cancelText?: string;
  danger?: boolean;
  loading?: boolean;
}

// ============================================================================
// Notification Types
// ============================================================================

export interface NotificationProps {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  closable?: boolean;
  onClose?: () => void;
}

export interface ToastProps extends Omit<NotificationProps, 'id'> {
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';
}

// ============================================================================
// Theme Types
// ============================================================================

export interface Theme {
  colors: {
    primary: Record<string, string>;
    success: Record<string, string>;
    warning: Record<string, string>;
    danger: Record<string, string>;
    gray: Record<string, string>;
  };
  spacing: Record<string, string>;
  borderRadius: Record<string, string>;
  fontSize: Record<string, string>;
  fontWeight: Record<string, string>;
  shadows: Record<string, string>;
  breakpoints: Record<string, string>;
}

// ============================================================================
// Context Types
// ============================================================================

export interface AppContextValue {
  theme: Theme;
  user?: {
    id: string;
    name: string;
    role: 'admin' | 'dispatcher' | 'driver' | 'viewer';
    permissions: string[];
  };
  notifications: NotificationProps[];
  addNotification: (notification: Omit<NotificationProps, 'id'>) => void;
  removeNotification: (id: string) => void;
}

export interface WebSocketContextValue {
  connected: boolean;
  connecting: boolean;
  error?: string;
  subscribe: (event: string, callback: (data: any) => void) => () => void;
  emit: (event: string, data: any) => void;
}

// ============================================================================
// Hook Return Types
// ============================================================================

export interface UseApiResult<T = any> {
  data?: T;
  loading: boolean;
  error?: string;
  refetch: () => Promise<void>;
}

export interface UsePaginationResult {
  current: number;
  pageSize: number;
  total: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
  goToPage: (page: number) => void;
  goToNext: () => void;
  goToPrev: () => void;
  changePageSize: (size: number) => void;
}

export interface UseLocalStorageResult<T> {
  value: T;
  setValue: (value: T | ((prev: T) => T)) => void;
  removeValue: () => void;
}