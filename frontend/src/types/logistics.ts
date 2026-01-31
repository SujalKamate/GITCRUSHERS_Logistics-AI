/**
 * TypeScript types for the Logistics AI system.
 * These match the Python Pydantic models in the backend.
 */

// ============================================================================
// Enums
// ============================================================================

export enum TruckStatus {
  IDLE = 'idle',
  EN_ROUTE = 'en_route',
  LOADING = 'loading',
  UNLOADING = 'unloading',
  MAINTENANCE = 'maintenance',
  STUCK = 'stuck',
  DELAYED = 'delayed',
}

export enum TrafficLevel {
  FREE_FLOW = 'free_flow',
  LIGHT = 'light',
  MODERATE = 'moderate',
  HEAVY = 'heavy',
  STANDSTILL = 'standstill',
}

export enum LoadPriority {
  LOW = 'low',
  NORMAL = 'normal',
  HIGH = 'high',
  URGENT = 'urgent',
  CRITICAL = 'critical',
}

export enum ActionType {
  REROUTE = 'reroute',
  REASSIGN = 'reassign',
  DISPATCH = 'dispatch',
  WAIT = 'wait',
  NOTIFY = 'notify',
  ESCALATE = 'escalate',
}

export enum ControlLoopPhase {
  OBSERVE = 'observe',
  REASON = 'reason',
  PLAN = 'plan',
  DECIDE = 'decide',
  ACT = 'act',
  FEEDBACK = 'feedback',
}

// ============================================================================
// Core Data Models
// ============================================================================

export interface Location {
  latitude: number;
  longitude: number;
  address?: string;
  name?: string;
}

export interface GPSReading {
  truck_id: string;
  timestamp: string;
  location: Location;
  speed_kmh: number;
  heading: number;
  accuracy_meters: number;
}

export interface Truck {
  id: string;
  name: string;
  status: TruckStatus;
  current_location?: Location;
  current_load_id?: string;
  driver_id?: string;
  capacity_kg: number;
  fuel_level_percent: number;
  last_gps_reading?: GPSReading;
  total_distance_km: number;
  total_deliveries: number;
}

export interface RoutePoint {
  location: Location;
  sequence: number;
  estimated_arrival?: string;
  actual_arrival?: string;
  is_waypoint: boolean;
  is_destination: boolean;
}

export interface Route {
  id: string;
  truck_id: string;
  origin: Location;
  destination: Location;
  waypoints: RoutePoint[];
  estimated_distance_km: number;
  estimated_duration_minutes: number;
  estimated_fuel_consumption_liters: number;
  started_at?: string;
  completed_at?: string;
  actual_distance_km?: number;
}

export interface Load {
  id: string;
  description: string;
  weight_kg: number;
  volume_m3?: number;
  priority: LoadPriority;
  pickup_location: Location;
  delivery_location: Location;
  pickup_window_start?: string;
  pickup_window_end?: string;
  delivery_deadline?: string;
  assigned_truck_id?: string;
  assigned_route_id?: string;
  picked_up_at?: string;
  delivered_at?: string;
}

export interface TrafficCondition {
  segment_id: string;
  level: TrafficLevel;
  speed_kmh: number;
  delay_minutes: number;
  incident_description?: string;
  affected_routes: string[];
  timestamp: string;
}

// ============================================================================
// Analysis and Reasoning Models
// ============================================================================

export interface Issue {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  affected_truck_ids: string[];
  affected_load_ids: string[];
  detected_at: string;
  metadata: Record<string, any>;
}

export interface ReasoningResult {
  situation_summary: string;
  issues: Issue[];
  risk_assessment: string;
  recommendations: string[];
  confidence: number;
  reasoning_trace: string[];
}

// ============================================================================
// Planning Models
// ============================================================================

export interface Scenario {
  id: string;
  name: string;
  description: string;
  actions: Record<string, any>[];
  estimated_cost: number;
  estimated_time_minutes: number;
  estimated_fuel_liters: number;
  reliability_score: number;
  simulation_parameters: Record<string, any>;
  simulation_results: Record<string, any>;
}

export interface PlanningResult {
  issue_id?: string;
  scenarios: Scenario[];
  comparison_matrix: Record<string, Record<string, number>>;
  recommended_scenario_id?: string;
}

// ============================================================================
// Decision Models
// ============================================================================

export interface Decision {
  id: string;
  scenario_id: string;
  action_type: ActionType;
  parameters: Record<string, any>;
  score: number;
  confidence: number;
  rationale: string;
  llm_verified: boolean;
  human_approved: boolean;
  decided_at: string;
}

export interface DecisionResult {
  selected_decision?: Decision;
  alternatives: Decision[];
  requires_human_approval: boolean;
  decision_trace: string[];
}

// ============================================================================
// Action Models
// ============================================================================

export interface ActionResult {
  action_id: string;
  decision_id: string;
  success: boolean;
  message: string;
  executed_at: string;
  details: Record<string, any>;
  rollback_possible: boolean;
}

export interface Notification {
  id: string;
  recipient_type: 'driver' | 'dispatcher' | 'customer' | 'system';
  recipient_id: string;
  subject: string;
  message: string;
  priority: string;
  sent_at?: string;
  delivered: boolean;
}

// ============================================================================
// Feedback Models
// ============================================================================

export interface OutcomeMetrics {
  decision_id: string;
  predicted_time_minutes: number;
  actual_time_minutes?: number;
  predicted_cost: number;
  actual_cost?: number;
  success?: boolean;
  deviation_percent?: number;
}

export interface LearningUpdate {
  parameter_name: string;
  old_value: number;
  new_value: number;
  reason: string;
  applied_at: string;
}

export interface FeedbackResult {
  outcomes: OutcomeMetrics[];
  learning_updates: LearningUpdate[];
  system_health: string;
  recommendations: string[];
}

// ============================================================================
// System State
// ============================================================================

export interface SystemState {
  trucks: Truck[];
  routes: Route[];
  loads: Load[];
  traffic_conditions: TrafficCondition[];
  active_issues: Issue[];
  pending_decisions: Decision[];
  recent_actions: ActionResult[];
  recent_outcomes: OutcomeMetrics[];
  last_updated: string;
  total_cycles_completed: number;
}

// ============================================================================
// Control Loop State
// ============================================================================

export interface ControlLoopState {
  current_phase: ControlLoopPhase;
  cycle_id: string;
  trucks: Truck[];
  routes: Route[];
  loads: Load[];
  traffic_conditions: TrafficCondition[];
  gps_readings: GPSReading[];
  observation_timestamp: string;
  reasoning_result?: ReasoningResult;
  current_issues: Issue[];
  planning_result?: PlanningResult;
  scenarios: Scenario[];
  decision_result?: DecisionResult;
  selected_decision?: Decision;
  action_results: ActionResult[];
  notifications_sent: Notification[];
  feedback_result?: FeedbackResult;
  continue_loop: boolean;
  requires_human_intervention: boolean;
  error_message?: string;
  cycle_start_time: string;
  cycle_end_time?: string;
  total_cycles: number;
}