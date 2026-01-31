/**
 * API-related types for the Logistics AI system.
 * Defines request/response interfaces and API endpoints.
 */

import { 
  SystemState, 
  ControlLoopState, 
  Truck, 
  Route, 
  Load, 
  TrafficCondition,
  Decision,
  ActionResult 
} from './logistics';

// ============================================================================
// API Response Wrappers
// ============================================================================

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// ============================================================================
// Fleet Management API
// ============================================================================

export interface FleetStatusResponse {
  trucks: Truck[];
  active_routes: Route[];
  pending_loads: Load[];
  traffic_conditions: TrafficCondition[];
  summary: {
    total_trucks: number;
    active_trucks: number;
    idle_trucks: number;
    trucks_with_issues: number;
    total_loads: number;
    pending_loads: number;
    in_transit_loads: number;
    delivered_loads: number;
  };
}

export interface TruckUpdateRequest {
  truck_id: string;
  status?: string;
  location?: {
    latitude: number;
    longitude: number;
  };
  fuel_level_percent?: number;
}

// ============================================================================
// Control Loop API
// ============================================================================

export interface ControlLoopStatusResponse {
  current_state: ControlLoopState;
  is_running: boolean;
  last_cycle_duration_ms: number;
  average_cycle_duration_ms: number;
  cycles_per_minute: number;
  uptime_seconds: number;
}

export interface StartControlLoopRequest {
  max_cycles?: number;
  cycle_interval_seconds?: number;
  auto_approve_decisions?: boolean;
}

export interface StopControlLoopRequest {
  reason?: string;
  immediate?: boolean;
}

// ============================================================================
// Decision Management API
// ============================================================================

export interface PendingDecisionsResponse {
  decisions: Decision[];
  requires_human_approval: Decision[];
  auto_approved: Decision[];
  rejected: Decision[];
}

export interface ApproveDecisionRequest {
  decision_id: string;
  approved: boolean;
  reason?: string;
  modifications?: Record<string, any>;
}

export interface DecisionHistoryResponse {
  decisions: (Decision & {
    outcome?: ActionResult;
    effectiveness_score?: number;
  })[];
  total: number;
  success_rate: number;
  average_confidence: number;
}

// ============================================================================
// Route Optimization API
// ============================================================================

export interface RouteOptimizationRequest {
  truck_id: string;
  current_location: {
    latitude: number;
    longitude: number;
  };
  destination: {
    latitude: number;
    longitude: number;
  };
  constraints?: {
    avoid_traffic?: boolean;
    minimize_fuel?: boolean;
    minimize_time?: boolean;
    max_detour_km?: number;
  };
}

export interface RouteOptimizationResponse {
  original_route: {
    distance_km: number;
    duration_minutes: number;
    fuel_liters: number;
    cost: number;
  };
  optimized_route: {
    distance_km: number;
    duration_minutes: number;
    fuel_liters: number;
    cost: number;
    waypoints: Array<{
      latitude: number;
      longitude: number;
      instruction?: string;
    }>;
  };
  savings: {
    time_minutes: number;
    fuel_liters: number;
    cost: number;
    distance_km: number;
  };
  confidence: number;
}

// ============================================================================
// Analytics API
// ============================================================================

export interface FleetAnalyticsResponse {
  time_period: {
    start: string;
    end: string;
  };
  metrics: {
    total_distance_km: number;
    total_fuel_consumed_liters: number;
    total_deliveries: number;
    average_utilization_percent: number;
    on_time_delivery_rate: number;
    fuel_efficiency_km_per_liter: number;
    cost_per_km: number;
    revenue_per_km: number;
  };
  trends: {
    daily_distance: Array<{ date: string; distance_km: number }>;
    daily_fuel: Array<{ date: string; fuel_liters: number }>;
    daily_deliveries: Array<{ date: string; deliveries: number }>;
    hourly_utilization: Array<{ hour: number; utilization_percent: number }>;
  };
  top_performers: {
    trucks: Array<{
      truck_id: string;
      truck_name: string;
      efficiency_score: number;
      total_distance_km: number;
      deliveries: number;
    }>;
  };
}

export interface IssueAnalyticsResponse {
  time_period: {
    start: string;
    end: string;
  };
  issue_summary: {
    total_issues: number;
    resolved_issues: number;
    pending_issues: number;
    critical_issues: number;
  };
  issue_types: Array<{
    type: string;
    count: number;
    average_resolution_time_minutes: number;
    impact_score: number;
  }>;
  resolution_trends: Array<{
    date: string;
    issues_created: number;
    issues_resolved: number;
  }>;
}

// ============================================================================
// WebSocket Event Types
// ============================================================================

export interface WebSocketMessage<T = any> {
  type: string;
  data: T;
  timestamp: string;
  source: 'control_loop' | 'fleet_manager' | 'decision_engine' | 'user';
}

export interface TruckLocationUpdate {
  truck_id: string;
  location: {
    latitude: number;
    longitude: number;
  };
  speed_kmh: number;
  heading: number;
  timestamp: string;
}

export interface IssueAlert {
  issue_id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  affected_trucks: string[];
  requires_action: boolean;
}

export interface DecisionNotification {
  decision_id: string;
  action_type: string;
  description: string;
  confidence: number;
  requires_approval: boolean;
  auto_execute_in_seconds?: number;
}

export interface ControlLoopUpdate {
  cycle_id: string;
  phase: string;
  progress_percent: number;
  current_action?: string;
  issues_detected: number;
  decisions_pending: number;
}

// ============================================================================
// Error Types
// ============================================================================

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
}

export interface ValidationError {
  field: string;
  message: string;
  value?: any;
}

// ============================================================================
// Configuration Types
// ============================================================================

export interface SystemConfiguration {
  control_loop: {
    cycle_interval_seconds: number;
    max_cycles_per_run: number;
    auto_approve_low_risk_decisions: boolean;
    human_approval_timeout_seconds: number;
  };
  fleet: {
    default_fuel_capacity_liters: number;
    default_speed_kmh: number;
    fuel_efficiency_km_per_liter: number;
    maintenance_interval_km: number;
  };
  routing: {
    traffic_update_interval_seconds: number;
    max_detour_percent: number;
    prefer_highways: boolean;
    avoid_toll_roads: boolean;
  };
  notifications: {
    email_alerts: boolean;
    sms_alerts: boolean;
    webhook_url?: string;
    alert_thresholds: {
      fuel_level_percent: number;
      delay_minutes: number;
      cost_increase_percent: number;
    };
  };
}